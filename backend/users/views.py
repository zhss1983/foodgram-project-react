from djoser import views

from .serializers import MyTokenCreateSerializer

class TokenCreateView(views.TokenCreateView):
    serializer_class = MyTokenCreateSerializer
