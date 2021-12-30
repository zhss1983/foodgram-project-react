from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=100),
    'AUTH_HEADER_TYPES': ('Token',),
}

DJOSER = {
#    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
#    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
#    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'users.serializers.UserCreateSerializer',
        'current_user': 'api.serializers.UseridSerializer',
        'user': 'api.serializers.UseridSerializer'
    },
#    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
#    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
#    'ACTIVATION_URL': '#/activate/{uid}/{token}',
#    'SEND_ACTIVATION_EMAIL': True,
    'LOGIN_FIELD': 'email',
}


