from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from rest_framework import exceptions, serializers
from djoser.conf import settings

User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
#    class Meta:
#        model = User
#        fields = tuple(User.REQUIRED_FIELDS) + (
#            'username',)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
#            settings.USER_ID_FIELD,
            "password", 'username',
        )


class UseridSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'username', settings.USER_ID_FIELD)


class MyTokenCreateSerializer(TokenCreateSerializer):
    def __init__(self, *args, **kwargs):
        #email = kwargs['data'].get('email')
        #user = get_object_or_404(User, email=email)
        #kwargs['data']['username'] = user.username
        super().__init__(*args, **kwargs)

"""from .models import User

class MyTokenCreateSerializer(TokenCreateSerializer):
    def __init__(self, *args, **kwargs):
        #email = kwargs['data'].get('email')
        #user = get_object_or_404(User, email=email)
        #kwargs['data']['username'] = user.username
#        kwargs['data'].pop('email')

        super().__init__(*args, **kwargs)
"""