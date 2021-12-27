from django.contrib.auth.models import AnonymousUser
import base64
from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)
from django.db import transaction

import copy
import inspect
import traceback
from collections import OrderedDict, defaultdict
from collections.abc import Mapping

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.db.models.fields import Field as DjangoModelField
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from rest_framework.compat import postgres_fields
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.fields import get_error_detail, set_value
from rest_framework.settings import api_settings
from rest_framework.utils import html, model_meta, representation
from rest_framework.utils.field_mapping import (
    ClassLookupDict, get_field_kwargs, get_nested_relation_kwargs,
    get_relation_kwargs, get_url_kwargs
)
from rest_framework.utils.serializer_helpers import (
    BindingDict, BoundField, JSONBoundField, NestedBoundField, ReturnDict,
    ReturnList
)
from rest_framework.validators import (
    UniqueForDateValidator, UniqueForMonthValidator, UniqueForYearValidator,
    UniqueTogetherValidator
)


from rest_framework.fields import (  # NOQA # isort:skip
    BooleanField, CharField, ChoiceField, DateField, DateTimeField, DecimalField,
    DictField, DurationField, EmailField, Field, FileField, FilePathField, FloatField,
    HiddenField, HStoreField, IPAddressField, IntegerField, JSONField,
    ListField, ModelField, MultipleChoiceField, NullBooleanField, ReadOnlyField,
    RegexField, SerializerMethodField, SlugField, TimeField, URLField, UUIDField,
    #ImageField
)
from rest_framework.relations import (  # NOQA # isort:skip
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField, StringRelatedField,
)

# Non-field imports, but public API
from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)
from rest_framework.relations import Hyperlink, PKOnlyObject  # NOQA # isort:skip
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    SerializerMethodField, ValidationError, CurrentUserDefault,
    ModelSerializer, SlugRelatedField, DecimalField, raise_errors_on_nested_writes,
    ImageField
)
from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator
from .models import Follow, Tag, Ingredient, Recipe, Favorite, Amount, TagRecipe
from users.models import User
from users.serializers import UserCreateSerializer, UseridSerializer
from .default import GetRecipesLimit, GetQueryParameter

VALIDATION_ERROR_MESSAGE = ('Отсутствует обязательное поле в теле запроса или'
                            ' оно не соответствует требованиям')

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'slug', 'color')


class TagRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='tag.id')
    name = ReadOnlyField(source='tag.name')
    color = ReadOnlyField(source='tag.color')
    slug = ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        if isinstance(data, int):
            return Tag.objects.get(pk=data)
        return data

class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class UseridSerializer(UseridSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = UseridSerializer.Meta.fields + (
            'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = CurrentUserDefault()(self)
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowEditSerializer(UseridSerializer):
    recipes = SerializerMethodField()  # RecipeFollowers(many=True)
    recipes_count = SerializerMethodField()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        if queryset:
            limit = GetRecipesLimit()(self)
            limit = ''.join(char for char in limit if char in '0123456789')
            if limit:
                queryset = queryset[:int(limit)]
        serializer = RecipeFollowers(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta(UseridSerializer.Meta):
        fields = UseridSerializer.Meta.fields + ('recipes', 'recipes_count')
        model = User


class AmountSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.pk')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, required=True)
    ingredients = AmountSerializer(many=True, required=True)
#    tags = PrimaryKeyRelatedField(
#        many=True, required=True, queryset=Tag.objects.all())
    author = UseridSerializer(default=CurrentUserDefault())
#    ingredients = AmountSaveSerializer(many=True, required=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(required=True)
    cooking_time = IntegerField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')
        read_only_fields = ('id', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return False  # obj.selected

    def get_is_in_shopping_cart(self, obj):
        return False  # Follow.objects.filter(user=obj).exists()

    def validate_cooking_time(self, value):
        if not isinstance(value, int):
            raise ValidationError('This field must be integer value.')
        if value < 1:
            raise ValidationError('This field must be >= 1.')
        return value

#    def validate_tags(self, value):
#        #if self.context['request'].method != SAFE_METHODS:
#        if not isinstance(value, int):
#            raise ValidationError(f'Недопустимые данные. Ожидался int, но был получен {type(value)}.')
#        return value


    @transaction.atomic
    def create(self, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data.pop('author')
        author = CurrentUserDefault()(self)

        recipe = Recipe.objects.create(author=author, **validated_data)

        ings = [None] * len(ingredients)
        for pos, obj in enumerate(ingredients):
            amount = obj['amount']
            ing = get_object_or_404(Ingredient, pk=obj['ingredient']['pk'])
            ings[pos] = Amount(recipe=recipe, amount=amount, ingredient=ing)
        Amount.objects.bulk_create(ings)

        tagrecipe = [None] * len(tags)
        for pos, tag in enumerate(tags):
            tagrecipe[pos] = TagRecipe(recipe=recipe, tag=tag)
        TagRecipe.objects.bulk_create(tagrecipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):

        tags = validated_data.pop('tags')
        old_tags = Tag.objects.filter(tagrecipes__recipe=instance).all()
        #old_tags = instance.tags.all()
        #old_tags = TagRecipe.objects.filter(recipe=instance).tag.all()

        del_tags = tuple(tag for tag in old_tags if tag not in tags)
        new_tags = tuple(tag for tag in tags if tag not in old_tags)

        TagRecipe.objects.filter(tag__in=del_tags, recipe=instance).delete()

        tagrecipe = [None] * len(new_tags)
        for pos, tag in enumerate(new_tags):
            tagrecipe[pos] = TagRecipe(recipe=instance, tag=tag)
        TagRecipe.objects.bulk_create(tagrecipe)


        ingredients = validated_data.pop('ingredients')
        old_ings = instance.ingredients.all()

#        while ingredients:
#            obj = ingredients.pop()
#            amount = obj['amount']
#            ing = get_object_or_404(Ingredient, pk=obj['ingredient']['pk'])
#            obj, create = old_ings.get_or_create(
#            #obj, create=Amount.objects.get_or_create(
#                recipe=instance, amount=amount, ingredient=ing)

        new_ings = [None] * len(ingredients)
        for pos, obj in enumerate(ingredients):
            amount = obj['amount']
            ing = get_object_or_404(Ingredient, pk=obj['ingredient']['pk'])
            obj, create = old_ings.get_or_create(
            #obj, create=Amount.objects.get_or_create(
                recipe=instance, amount=amount, ingredient=ing)
            new_ings[pos] = obj

        #del_ings = []
        for ing in old_ings:
            if ing not in new_ings:
                #del_ings.append(ing)
                ing.delete()
        
        #Amount.objects.filter(pk__in)
        #Amount.objects.bulk_create(ings)

        if 'image' in validated_data:
            instance.image.delete()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeSaveSerializer(RecipeSerializer):
    tags = TagRecipeSerializer(many=True, required=True)

class RecipeFollowers(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(ModelSerializer):
    # user = SlugRelatedField(
    #    slug_field='username', queryset=User.objects.all())
    # author = UsersSerializer(read_only=True)
    author = FollowEditSerializer()

    class Meta:
        fields = ('author',)
        model = Follow
