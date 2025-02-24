from django_filters import rest_framework as filters
from .models import Game, Franchise, Character, Review, News


class GameFilter(filters.FilterSet):
    platforms = filters.CharFilter(field_name="platforms", lookup_expr="icontains")
    themes = filters.CharFilter(field_name="themes", lookup_expr="icontains")
    concepts = filters.CharFilter(field_name="concepts", lookup_expr="icontains")
    genres = filters.CharFilter(field_name="genres", lookup_expr="icontains")
    release_date = filters.CharFilter(
        field_name="release_date", lookup_expr="icontains"
    )
    developers = filters.CharFilter(field_name="developers", lookup_expr="icontains")
    is_casual = filters.BooleanFilter(field_name="is_casual")
    is_popular = filters.BooleanFilter(field_name="is_popular")
    average_score = filters.NumberFilter(field_name="average_score", lookup_expr="gte")
    franchises = filters.CharFilter(field_name="franchises", lookup_expr="icontains")

    class Meta:
        model = Game
        fields = [
            "platforms",
            "themes",
            "concepts",
            "genres",
            "release_date",
            "developers",
            "is_casual",
            "is_popular",
            "average_score",
            "franchises",
        ]


class FranchiseFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    games = filters.CharFilter(field_name="games", lookup_expr="icontains")
    games_count = filters.NumberFilter(field_name="games_count", lookup_expr="gte")

    class Meta:
        model = Franchise
        fields = ["title", "games", "games_count"]


class CharacterFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    birthday = filters.CharFilter(field_name="birthday", lookup_expr="icontains")
    friends = filters.CharFilter(field_name="friends", lookup_expr="icontains")
    enemies = filters.CharFilter(field_name="enemies", lookup_expr="icontains")
    games = filters.CharFilter(field_name="games", lookup_expr="icontains")
    first_game = filters.CharFilter(field_name="first_game", lookup_expr="icontains")
    franchises = filters.CharFilter(field_name="franchises", lookup_expr="icontains")

    class Meta:
        model = Character
        fields = [
            "name",
            "birthday",
            "friends",
            "enemies",
            "games",
            "first_game",
            "franchises",
        ]


class GameReviewFilter(filters.FilterSet):
    game = filters.CharFilter(field_name="game__guid", lookup_expr="exact")
    reviewers = filters.CharFilter(field_name="reviewers", lookup_expr="icontains")
    score = filters.NumberFilter(field_name="score", lookup_expr="exact")
    min_score = filters.NumberFilter(field_name="score", lookup_expr="gte")
    max_score = filters.NumberFilter(field_name="score", lookup_expr="lte")
    date_added = filters.DateTimeFilter(field_name="date_added", lookup_expr="date")

    class Meta:
        model = Review
        fields = ["game", "reviewers", "score", "min_score", "max_score", "date_added"]


class NewsFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    publish_date = filters.CharFilter(
        field_name="publish_date", lookup_expr="icontains"
    )
    platforms = filters.CharFilter(field_name="platforms", lookup_expr="icontains")

    class Meta:
        model = News
        fields = ["title", "publish_date", "platforms"]
