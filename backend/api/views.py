from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.filters import SearchFilter
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .default import get_param_value_views, getlist_param_value_views
from .filters import NameSearchFilter
from .models import Favorite, Follow, Ingredient, Recipe, Tag, Trolley
from .permissions import (
    AdminOrReadOnly, EditAccessOrReadOnly, RegistrationUserPermission)
from .serializers import (
    FavoriteSerializer, FollowEditSerializer, IngredientSerializer,
    RecipeSaveSerializer, RecipeSerializer, TagSerializer, UseridSerializer)
from users.pagination import LimitPageNumberPagination
from users.models import User


class UsersViewSet(GenericViewSet, RetrieveModelMixin):
    permission_classes = (RegistrationUserPermission, )  # RegistrationUserPermission AllowAny
    filter_backends = (SearchFilter, )
    search_fields = ('=username', '=email')
    serializer_class = UseridSerializer
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination
    metadata_class = ('GET', )

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=['GET'],
            url_path='me')
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (SearchFilter, )
    search_fields = ('=name', )
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    permission_classes = (AdminOrReadOnly, )
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (NameSearchFilter, )
    pagination_class = None
    search_fields = ('$name', )  # '^name',


class SubscribeViewSet(GenericViewSet, RetrieveModelMixin):
    permission_classes = (EditAccessOrReadOnly, )  # EditAccessOrReadOnly AllowAny
    serializer_class = FollowEditSerializer
    lookup_value_regex = r'\d+'
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(following__user=self.request.user).all()
        return User.objects.all()

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=['GET'],
            url_path='subscriptions')
    def follow_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['POST', 'DELETE'],
            url_path='subscribe')
    def follow(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=self.get_id())
        if request.method == 'POST':
            if author == self.request.user:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance, created = Follow.objects.get_or_create(
                                    user=self.request.user, author=author)
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(instance.author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            instance = Follow.objects.filter(
                user=self.request.user, author=author)
            if not instance.exists():
                return Response(
                    {"errors": "Ошибка отписки"},
                    status=status.HTTP_204_NO_CONTENT
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_id(self):
        return self.kwargs[self.lookup_field]


class RecipeViewSet(ModelViewSet):
    permission_classes = (EditAccessOrReadOnly, )
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination

    def get_is_favorited(self):
        value = get_param_value_views(self, 'is_favorited')
        if value is not None:
            return False if value == '0' else True

    def get_is_in_shopping_cart(self):
        value = get_param_value_views(self, 'is_in_shopping_cart')
        if value is not None:
            return False if value == '0' else True

    def get_author(self):
        id = get_param_value_views(self, 'author')
        if id:
            if id.isdigit():
                return get_object_or_404(User, pk=id)
            if isinstance(id, str):
                return get_object_or_404(User, username=id)

    def get_tags(self):
        return getlist_param_value_views(self, 'tags')

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related(
            'selected', 'trolley', 'author', 'tags')
        is_favorited = self.get_is_favorited()
        if is_favorited is not None:
            if is_favorited:
                queryset = queryset.filter(selected__user=self.request.user)
            else:
                queryset = queryset.filter(
                    ~Q(selected__user=self.request.user))
        is_in_shopping_cart = self.get_is_in_shopping_cart()
        if is_in_shopping_cart is not None:
            if is_in_shopping_cart:
                queryset = queryset.filter(trolley__user=self.request.user)
            else:
                queryset = queryset.filter(
                    ~Q(trolley__user=self.request.user))
        author = self.get_author()
        if author:
            queryset = queryset.filter(author=author)
        tags = self.get_tags()
        if tags:
            queryset = queryset.filter(tags__tag__slug__in=tags)
        return queryset.order_by('-pk').distinct('pk').all()

    def get_serializer_class(self):
        if self.request.method == SAFE_METHODS:
            return RecipeSerializer
        else:
            return RecipeSaveSerializer

    @action(detail=True,
            permission_classes=[EditAccessOrReadOnly],
            methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.get_id())
        if request.method == 'POST':
            instance, created = Favorite.objects.get_or_create(
                                    user=self.request.user, recipe=recipe)
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Favorite.objects.filter(
                user=self.request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_id(self):
        return self.kwargs[self.lookup_field]

    @action(detail=False,
            permission_classes=[EditAccessOrReadOnly],
            methods=['GET'])
    def download_shopping_cart(self, request, *args, **kwargs):
        trolleys = Trolley.objects.filter(
            user=self.request.user).select_related('recipe').prefetch_related(
            'recipe__ingredients', 'recipe__ingredients__ingredient').all()
        ingredients = dict()
        for trolley in trolleys:
            for ingredient in trolley.recipe.ingredients.all():
                ingredients[ingredient.ingredient] = ingredients.get(
                    ingredient.ingredient, 0) + ingredient.amount
        shopping_cart = ['Список необходимых покупок:']
        pos = 0
        ingredients = sorted(
            ingredients.items(), key=lambda value: value[0].name)
        for key, value in ingredients:
            pos += 1
            shopping_cart.append(
                f'{pos}: {key.name}, {float(value)} {key.measurement_unit}')
        return FileResponse(
            '\n'.join(shopping_cart),
            as_attachment=True,
            filename='shopping_cart.txt',
            status=status.HTTP_200_OK
        )

    @action(detail=True,
            permission_classes=[EditAccessOrReadOnly],
            methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.get_id())
        if request.method == 'POST':
            instance, created = Trolley.objects.get_or_create(
                                    user=self.request.user, recipe=recipe)
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Trolley.objects.filter(
                user=self.request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
