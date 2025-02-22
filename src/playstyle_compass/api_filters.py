from django_filters import rest_framework as filters
from .models import Game

class GameFilter(filters.FilterSet):
    platforms = filters.CharFilter(field_name="platforms", lookup_expr="icontains")
    themes = filters.CharFilter(field_name="themes", lookup_expr="icontains")
    concepts = filters.CharFilter(field_name="concepts", lookup_expr="icontains")
    genres = filters.CharFilter(field_name="genres", lookup_expr="icontains")
    release_date = filters.CharFilter(field_name="release_date", lookup_expr="icontains")
    developers = filters.CharFilter(field_name="developers", lookup_expr="icontains")
    is_casual = filters.BooleanFilter(field_name="is_casual")
    is_popular = filters.BooleanFilter(field_name="is_popular")
    average_score = filters.NumberFilter(field_name="average_score", lookup_expr="gte")
    franchises = filters.CharFilter(field_name="franchises", lookup_expr="icontains")

    class Meta:
        model = Game
        fields = ['platforms', 'themes', 'concepts', 'genres', 'release_date', 'developers', 'is_casual', 'is_popular', 'average_score', 'franchises']