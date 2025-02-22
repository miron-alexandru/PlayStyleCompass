from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import generics
from .models import Game, Franchise, Character, Review, News
from .serializers import GameSerializer, FranchiseSerializer, CharacterSerializer, GameReviewSerializer, NewsSerializer
from .permissions import HasValidAPIKey
from .api_filters import GameFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination


class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [HasValidAPIKey]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = GameFilter
    ordering_fields = ['title', 'release_date', 'average_score']
    ordering = ['title']
    pagination_class = LimitOffsetPagination
    limit = 100

class GameDetailView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [HasValidAPIKey]

    def get_serializer(self, *args, **kwargs):
        """
        Override the get_serializer method to allow the 'fields' query parameter
        to filter the returned fields dynamically.
        """
        # Get the 'fields' query parameter if it exists
        fields = self.request.query_params.get('fields', None)
        
        # If 'fields' is provided, filter the fields in the serializer
        if fields:
            fields = fields.split(',')
            # Get the original serializer
            serializer_class = self.get_serializer_class()
            # Create a new serializer with only the requested fields
            kwargs['fields'] = fields
            return serializer_class(*args, **kwargs)
        
        return super().get_serializer(*args, **kwargs)

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


class GameReviewsListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = GameReviewSerializer
    permission_classes = [HasValidAPIKey]

class GameReviewsDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = GameReviewSerializer
    permission_classes = [HasValidAPIKey]

class NewsListView(generics.ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [HasValidAPIKey]

class NewsDetailView(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [HasValidAPIKey]










