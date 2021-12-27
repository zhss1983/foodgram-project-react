import os

from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=100),
    'AUTH_HEADER_TYPES': ('Token',),
}

SERIALIZERS = {
    'user_create': 'users.serializers.UserCreateSerializer',
    'current_user': 'users.serializers.UserCreateSerializer',
}

DJOSER = {
#    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
#    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
#    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'users.serializers.UserCreateSerializer',
        'current_user': 'users.serializers.UserCreateSerializer',
    },
#    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
#    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
#    'ACTIVATION_URL': '#/activate/{uid}/{token}',
#    'SEND_ACTIVATION_EMAIL': True,
    'LOGIN_FIELD': 'email',
}

