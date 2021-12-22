from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, SubscribeViewSet, UsersViewSet, RecipeViewSet

api_router_v1 = DefaultRouter()

#  http://localhost/api/tags/
#  http://localhost/api/tags/{id}/
api_router_v1.register('tags', TagViewSet, basename='tags')

#  http://localhost/api/ingredients/
#  http://localhost/api/ingredients/{id}/
#  http://localhost/api/ingredients/(?P<name>\.+)
api_router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')

#  http://localhost/api/users/subscriptions/
# api_router_v1.register('users/subscribe', FollowListViewSet, basename='subscriptions')

#  http://localhost/api/users/{pk}/subscribe/
api_router_v1.register('users1', SubscribeViewSet, basename='subscribe')

api_router_v1.register('users', UsersViewSet, basename='users')

#  http://localhost/api/recipes/
#  http://localhost/api/recipes/{id}/
#?  http://localhost/api/recipes/download_shopping_cart/
#?  http://localhost/api/recipes/{id}/shopping_cart/
#  http://localhost/api/recipes/{id}/favorite/
api_router_v1.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(api_router_v1.urls)),
]
