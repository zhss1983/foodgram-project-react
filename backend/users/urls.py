from django.urls import include, path, re_path

from .views import TokenCreateView

from djoser.views import TokenDestroyView, UserViewSet
from rest_framework.routers import DefaultRouter

#router = DefaultRouter()
#router.register("users", UserViewSet)

urlpatterns = [
    #re_path(r'^auth/token/login/?$', TokenCreateView.as_view(), name='login'),
    #re_path(r'^auth/token/logout/?$', TokenDestroyView.as_view(), name='logout'),
    path('auth/', include('djoser.urls.authtoken')),


#    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
