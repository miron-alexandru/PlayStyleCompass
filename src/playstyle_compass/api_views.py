from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import generics
from .models import Game
from .serializers import GameSerializer
from .permissions import HasValidAPIKey

class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [HasValidAPIKey]

class GameDetailView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [HasValidAPIKey]
