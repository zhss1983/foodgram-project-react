from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import TokenCreateSerializer

User = get_user_model()

class MyTokenCreateSerializer(TokenCreateSerializer):
    def __init__(self, *args, **kwargs):
        email = kwargs['data'].get('email')
        user = get_object_or_404(User, email=email)
        kwargs['data']['username'] = user.username
        super().__init__(*args, **kwargs)
