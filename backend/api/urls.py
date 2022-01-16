from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, RecipeViewSet, SubscribeViewSet, TagViewSet)

api_rout_v1 = DefaultRouter()
api_rout_v1.register(r'tags', TagViewSet, basename='tag')
api_rout_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')
api_rout_v1.register(r'users', SubscribeViewSet, basename='user')
api_rout_v1.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [path('', include(api_rout_v1.urls))]
