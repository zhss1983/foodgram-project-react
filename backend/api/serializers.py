from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import IntegerField, ReadOnlyField
from rest_framework.serializers import (
    CurrentUserDefault, ModelSerializer, SerializerMethodField,
    ValidationError)

from .default import get_param_value_serialize
from .models import (
    Amount, Favorite, Follow, Ingredient, Recipe, Tag, TagRecipe, Trolley)
from users.models import User
from users.serializers import UseridSerializer


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'slug', 'color')


class RecipeFollowers(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowEditSerializer(UseridSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        if queryset:
            limit = get_param_value_serialize(self, 'recipes_limit', '')
            limit = ''.join(char for char in limit if char in '0123456789')
            if limit:
                queryset = queryset[:int(limit)]
        serializer = RecipeFollowers(queryset, many=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
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

    @staticmethod
    def validate_amount(value):
        if value < 1:
            raise ValidationError('Количество должно не меньше 1.')
        return value


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, required=True)
    ingredients = AmountSerializer(many=True, required=True)
    author = UseridSerializer(default=CurrentUserDefault())
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
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Trolley.objects.filter(user=user, recipe=obj).exists()

    @staticmethod
    def validate_cooking_time(value):
        if value < 1:
            raise ValidationError('This field must be >= 1.')
        return value

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
        del_tags = tuple(tag for tag in old_tags if tag not in tags)
        new_tags = tuple(tag for tag in tags if tag not in old_tags)
        TagRecipe.objects.filter(tag__in=del_tags, recipe=instance).delete()
        tagrecipe = [None] * len(new_tags)
        for pos, tag in enumerate(new_tags):
            tagrecipe[pos] = TagRecipe(recipe=instance, tag=tag)
        TagRecipe.objects.bulk_create(tagrecipe)
        ingredients = validated_data.pop('ingredients')
        old_ings = instance.ingredients.all()
        new_ings = [None] * len(ingredients)
        for pos, obj in enumerate(ingredients):
            amount = obj['amount']
            ing = get_object_or_404(Ingredient, pk=obj['ingredient']['pk'])
            obj, create = old_ings.get_or_create(
                recipe=instance, amount=amount, ingredient=ing)
            new_ings[pos] = obj
        for ing in old_ings:
            if ing not in new_ings:
                ing.delete()
        if 'image' in validated_data:
            instance.image.delete()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeSaveSerializer(RecipeSerializer):
    tags = TagRecipeSerializer(many=True, required=True)
