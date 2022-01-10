from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=100),
    'AUTH_HEADER_TYPES': ('Token', )
}

DJOSER = {
    'PERMISSIONS': {
        'user_list': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    },
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'users.serializers.UserCreateSerializer',
        'current_user': 'api.serializers.UseridSerializer',
        'user': 'api.serializers.UseridSerializer'
    },
    'LOGIN_FIELD': 'email',
}
