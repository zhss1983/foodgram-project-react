from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from collections import OrderedDict
from functools import update_wrapper
from inspect import getmembers
from rest_framework.request import Request
from django.urls import NoReverseMatch
from django.utils.decorators import classonlymethod
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, views
from rest_framework.decorators import MethodMapper
from rest_framework.reverse import reverse
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from builtins import isinstance

from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet, ModelViewSet, ReadOnlyModelViewSet, ViewSet, ViewSetMixin)

from django.shortcuts import get_object_or_404


from .models import Follow, Tag, Recipe, Ingredient
from .serializers import TagSerializer, RecipeSerializer, IngredientSerializer, UsersSerializer, FollowEditSerializer, FollowSerializer
from .pagination import LimitPageNumberPagination

from users.models import User


class UsersViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('=username',)
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    @action(detail=False,
#            permission_classes=[IsAuthenticated],
            methods=['GET'],
            url_path='me')
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    #def me(self, request, *args, **kwargs):
    #    serializer = UsersSerializer(
    #        request.user, data=request.data, partial=True)
    #    serializer.is_valid()
    #    return Response(serializer.data)


class NameSearchFilter(SearchFilter):
    search_param = 'name'

class TagViewSet(ReadOnlyModelViewSet):  # (ListModelMixin, GenericViewSet):
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('=name',)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (NameSearchFilter, )
    pagination_class = None
    search_fields = ('^name',)


class SubscribeViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowEditSerializer
    lookup_field = 'id'
    lookup_value_regex = '\d+'
    queryset = User
    classmethod = ('GET', 'DELETE')
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    @action(detail=False,
            #permission_classes=[IsAuthenticated],
            methods=['GET'],
            url_path='subscribe')
    def follow_list(self, request, *args, **kwargs):
        recipes_limit = self.get_recipes_limit()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
#        if page is not None:
#            serializer = self.get_serializer(page, many=True)
#            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(page, many=True) # , limit=recipes_limit
        return self.get_paginated_response(serializer.data)
        #serializer = self.get_serializer(queryset, many=True) # , limit=recipes_limit
        #return Response(serializer.data)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['GET', 'DELETE'],
            url_path='subscribe')
    def follow(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=self.get_id())
        if request.method == 'GET':
            if author == self.request.user:
                return Response({"errors": "Ошибка подписки"}, status=status.HTTP_400_BAD_REQUEST)
            instance, created = Follow.objects.get_or_create(user=self.request.user, author=author)
            if not created:
                return Response({"errors": "Ошибка подписки"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(instance.author)
            #headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)#, headers=headers)
        elif request.method == 'DELETE':
            instance = Follow.objects.filter(user=self.request.user, author=author)
            if not instance.exists():
                return Response({"errors": "Ошибка отписки"}, status=status.HTTP_204_NO_CONTENT)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    def get_id(self):
        return self.kwargs[self.lookup_field]#.split('/')[0]

    def get_recipes_limit(self):
        return self.request.GET.get('recipes_limit', 3)


class RecipeViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer
    queryset = Recipe
    pagination_class = LimitPageNumberPagination

