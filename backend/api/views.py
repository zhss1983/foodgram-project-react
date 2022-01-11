from django.db.models import Q, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.filters import SearchFilter
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import NameSearchFilter, RecipeFilter
from .models import Favorite, Follow, Ingredient, Recipe, Tag, Trolley, Amount
from .permissions import (
    AdminOrReadOnly, EditAccessOrReadOnly, RegistrationUserPermission,
    AuthorOrAdminUserPermission)
from .serializers import (
    FavoriteSerializer, FollowEditSerializer, IngredientSerializer,
    RecipeSaveSerializer, RecipeSerializer, TagSerializer, UseridSerializer)
from users.pagination import LimitPageNumberPagination
from users.models import User


class UsersViewSet(GenericViewSet, RetrieveModelMixin):
    permission_classes = (RegistrationUserPermission, )
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


class PostDeletGetID:

    def get_id(self):
        return self.kwargs[self.lookup_field]


class TagViewSet(ModelViewSet):
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (SearchFilter, )
    search_fields = ('=name', )
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    lookup_value_regex = r'\d+'
    lookup_field = 'id'
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    permission_classes = (AdminOrReadOnly, )
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (NameSearchFilter, )
    pagination_class = None
    lookup_value_regex = r'\d+'
    lookup_field = 'id'
    search_fields = ('$name', )


class SubscribeViewSet(GenericViewSet, PostDeletGetID):
    permission_classes = (EditAccessOrReadOnly, )
    serializer_class = FollowEditSerializer
    lookup_value_regex = r'\d+'
    lookup_field = 'id'
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(following__user=self.request.user)
        return User.objects.all()

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=['GET'],
            url_path='subscriptions',
            url_name='subscriptions')
    def follow_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['POST', 'DELETE'],
            url_path='subscribe',
            url_name='subscribe')
    def follow(self, request, *args, **kwargs):
        """Добавление и удаление подписки на пользователя"""
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
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class RecipeViewSet(ModelViewSet, PostDeletGetID):
    filter_backends = (RecipeFilter, )
    permission_classes = (EditAccessOrReadOnly, )
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    lookup_value_regex = r'\d+'
    lookup_field = 'id'
    queryset = Recipe.objects.prefetch_related(
        'selected', 'trolley', 'author', 'tags')


    def get_serializer_class(self):
        if self.request.method == SAFE_METHODS:
            return RecipeSerializer
        else:
            return RecipeSaveSerializer

    @action(detail=False,
            permission_classes=[AuthorOrAdminUserPermission],
            methods=['GET'])
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_cart = ['Список необходимых покупок:']
        ingredients_list = Amount.objects.filter(
            recipe__trolley__user=self.request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')).order_by('ingredient__name').values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit')
        for pos, (key, value, unit) in enumerate(ingredients_list[1:]):
            shopping_cart.append(f'{pos}: {key}, {value} {unit}')
        return FileResponse(
            '\n'.join(shopping_cart),
            as_attachment=True,
            filename='shopping_cart.txt',
            status=status.HTTP_200_OK,
            content_type='text/plain'
        )

    def post_delete(self, request, target):
        obj = get_object_or_404(Recipe, pk=self.get_id())
        if request.method == 'POST':
            instance, created = target.objects.get_or_create(
                user=request.user, recipe=obj)
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            target.objects.filter(
                user=request.user, recipe=obj).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,
            permission_classes=[AuthorOrAdminUserPermission],
            methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        """Добавление и удаление из избранных"""
        return self.post_delete(request, Favorite)

    @action(detail=True,
            permission_classes=[AuthorOrAdminUserPermission],
            methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        """Добавление и удаление из корзины"""
        return self.post_delete(request, Trolley)
