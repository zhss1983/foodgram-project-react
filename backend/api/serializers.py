from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CurrentUserDefault, ModelSerializer, SlugRelatedField, SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow, Tag, Ingredient, Recipe
from users.models import User

VALIDATION_ERROR_MESSAGE = ('Отсутствует обязательное поле в теле запроса или'
                            ' оно не соответствует требованиям')


class UsersSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj).exists()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('__all__', 'is_favorited', 'is_in_shopping_cart')
        #fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
        #          'text', 'cooking_time', 'is_favorited',
        #          'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return obj.selected

    def get_is_in_shopping_cart(self, obj):
        return False  #  Follow.objects.filter(user=obj).exists()

    def validate_cooking_time(self, value):
        if not isinstance(value, int):
            raise ValidationError('This field must be integer value.')
        if value < 1:
            raise ValidationError('This field must be >= 1.')




class FollowEditSerializer(UsersSerializer):
    #pass
    #recipes = RecipeSerializer(many=True, read_only=True)
    #recipes = SerializerMethodField()
    recipes = RecipeSerializer()
    recipes_count = SerializerMethodField()

    def get_recipes(self, obj):
        return Recipe.objects.filter(author=obj)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

#    def get_recipes_count(self, obj):
#        return Recipe.objects.filter(author=obj).count()

    class Meta(UsersSerializer.Meta):
        fields = (*UsersSerializer.Meta.fields, 'recipes', 'recipes_count')
#        fields = (*UsersSerializer.Meta.fields, 'recipes_count')

class FollowSerializer(ModelSerializer):
    #user = SlugRelatedField(
    #    slug_field='username', queryset=User.objects.all())
    # author = UsersSerializer(read_only=True)
    author = FollowEditSerializer(read_only=True)

    class Meta:
        fields = ('author',)
        model = Follow


