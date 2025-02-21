from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import generics
from .models import Game, Franchise, Character
from .serializers import GameSerializer, FranchiseSerializer, CharacterSerializer
from .permissions import HasValidAPIKey

class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [HasValidAPIKey]

class GameDetailView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [HasValidAPIKey]

class FranchiseListView(generics.ListAPIView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer
    permission_classes = [HasValidAPIKey]

class FranchiseDetailView(generics.RetrieveAPIView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer
    permission_classes = [HasValidAPIKey]

class CharacterListView(generics.ListAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [HasValidAPIKey]

class CharacterDetailView(generics.RetrieveAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [HasValidAPIKey]









