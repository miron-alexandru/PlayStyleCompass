from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import generics
from .models import Game, Franchise, Character, Review, News
from .serializers import (
    GameSerializer,
    FranchiseSerializer,
    CharacterSerializer,
    GameReviewSerializer,
    NewsSerializer,
)
from .permissions import HasValidAPIKey
from .api_filters import (
    GameFilter,
    FranchiseFilter,
    CharacterFilter,
    GameReviewFilter,
    NewsFilter,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination


class BaseListView(generics.ListAPIView):
    """Base class for list views with filtering, ordering, and pagination."""

    permission_classes = [HasValidAPIKey]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = LimitOffsetPagination
    limit = 100


class BaseDetailView(generics.RetrieveAPIView):
    """Base class for detail views with dynamic field filtering."""

    permission_classes = [HasValidAPIKey]

    def get_serializer(self, *args, **kwargs):
        fields = self.request.query_params.get("fields", None)
        if fields:
            kwargs["fields"] = fields.split(",")
        return super().get_serializer(*args, **kwargs)


class GameListView(BaseListView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filterset_class = GameFilter
    ordering_fields = ["title", "release_date", "average_score"]
    ordering = ["title"]


class GameDetailView(BaseDetailView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class FranchiseListView(BaseListView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer
    filterset_class = FranchiseFilter
    ordering_fields = ["title", "games_count"]
    ordering = ["title"]


class FranchiseDetailView(BaseDetailView):
    queryset = Franchise.objects.all()
    serializer_class = FranchiseSerializer


class CharacterListView(BaseListView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    filterset_class = CharacterFilter
    ordering_fields = ["name"]
    ordering = ["name"]


class CharacterDetailView(BaseDetailView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer


class GameReviewsListView(BaseListView):
    queryset = Review.objects.all()
    serializer_class = GameReviewSerializer
    filterset_class = GameReviewFilter
    ordering_fields = ["score", "likes", "dislikes", "review_deck", "date_added"]
    ordering = ["date_added"]


class GameReviewsDetailView(BaseDetailView):
    queryset = Review.objects.all()
    serializer_class = GameReviewSerializer


class NewsListView(BaseListView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filterset_class = NewsFilter
    ordering_fields = ["title", "publish_date"]
    ordering = ["title"]


class NewsDetailView(BaseDetailView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
