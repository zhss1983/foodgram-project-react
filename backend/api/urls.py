from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, SubscribeViewSet, UseridSerializer, RecipeViewSet

api_router_v1 = DefaultRouter()

#  http://localhost/api/tags/
#  http://localhost/api/tags/{id}/
api_router_v1.register(r'tags', TagViewSet, basename='tag')

#  http://localhost/api/ingredients/
#  http://localhost/api/ingredients/{id}/
#  http://localhost/api/ingredients/(?P<name>\.+)
api_router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')

#  http://localhost/api/users/subscriptions/
#  http://localhost/api/users/{pk}/subscribe/
api_router_v1.register(r'users', SubscribeViewSet, basename='subscribe')

#api_router_v1.register(r'users', UsersViewSet, basename='user-get')

#  http://localhost/api/recipes/
#  http://localhost/api/recipes/{id}/
#?  http://localhost/api/recipes/download_shopping_cart/
#?  http://localhost/api/recipes/{id}/shopping_cart/
#  http://localhost/api/recipes/{id}/favorite/
api_router_v1.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(api_router_v1.urls)),
]
