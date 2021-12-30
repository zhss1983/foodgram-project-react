from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from djoser.conf import settings

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            "password", 'username',
        )


class UseridSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'username', settings.USER_ID_FIELD)
