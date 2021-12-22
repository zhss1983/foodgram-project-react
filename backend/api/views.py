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
from .serializers import FollowSerializer, TagSerializer, RecipeSerializer, IngredientSerializer, UsersSerializer, FollowEditSerializer
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
            permission_classes=[IsAuthenticated],
            methods=['GET'])
    def me(self, request, *args, **kwargs):
        serializer = UsersSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid()
        return Response(serializer.data)


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


class RecipeViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class SubscribeViewSet(ModelViewSet): # ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer
    lookup_field = 'pk'
    lookup_value_regex = '\d+/subscribe'
    #queryset = Follow

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        kwarg = self.kwargs[lookup_url_kwarg].split('/')[0]

        filter_kwargs = {self.lookup_field: kwarg}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class FollowEditViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowEditSerializer
    #serializer_class = UsersSerializer
