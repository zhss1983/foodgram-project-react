from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.filters import SearchFilter

from users.models import User


class RecipeFilter:
    """
    A base class from which all filter backend classes should inherit.
    """

    def get_param_value_views(self, request, parameter_name, default=None):
        return request.query_params.get(parameter_name, default)

    def getlist_param_value_views(self, request, parameter_name, default=None):
        return request.query_params.getlist(parameter_name, default)

    def get_bool_by_name(self, request, name):
        value = self.get_param_value_views(request, name)
        if value is not None:
            return value != "0"
        return None

    def get_is_favorited(self, request):
        return self.get_bool_by_name(request, "is_favorited")

    def get_is_in_shopping_cart(self, request):
        return self.get_bool_by_name(request, "is_in_shopping_cart")

    def get_author(self, request):
        author_id = self.get_param_value_views(request, "author")
        if author_id:
            if author_id.isdigit():
                return get_object_or_404(User, pk=author_id)
            if isinstance(author_id, str):
                return get_object_or_404(User, username=author_id)
        return None

    def get_tags(self, request):
        return self.getlist_param_value_views(request, "tags")

    def filter_queryset(self, request, queryset, view):
        """
        Return a filtered queryset for Recipe model.
        """
        is_favorited = self.get_is_favorited(request)
        if is_favorited is not None:
            if is_favorited:
                queryset = queryset.filter(selected__user=request.user)
            else:
                queryset = queryset.filter(~Q(selected__user=request.user))
        is_in_shopping_cart = self.get_is_in_shopping_cart(request)
        if is_in_shopping_cart is not None:
            if is_in_shopping_cart:
                queryset = queryset.filter(trolley__user=request.user)
            else:
                queryset = queryset.filter(~Q(trolley__user=request.user))
        author = self.get_author(request)
        if author:
            queryset = queryset.filter(author=author)
        tags = self.get_tags(request)
        if tags:
            queryset = queryset.filter(tags__tag__slug__in=tags)
        return queryset.order_by("-pk").distinct("pk")


class NameSearchFilter(SearchFilter):
    search_param = "name"
