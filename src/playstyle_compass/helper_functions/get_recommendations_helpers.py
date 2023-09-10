"""
The 'get_recommendations_helpers' module contains helper functions used for
the get_recommendations view function."""

import re

from django.db.models import Q
from ..models import Game

def process_gaming_history(gaming_history, unique_games, unique_genres, matching_games):
    """Process the gaming history to find matching games and their genres."""
    for history_game in gaming_history:
        pattern = re.escape(history_game).replace(r'\ ', r'.*?')
        pattern = f'.*{pattern}.*'
        matching_title_games = Game.objects.filter(title__iregex=rf'^{pattern}')

        for matching_game in matching_title_games:
            if matching_game not in unique_games:
                unique_games.add(matching_game)

                if matching_game.genres:
                    unique_genres.add(matching_game.genres)
                    matching_genre_games = Game.objects.filter(genres__icontains=matching_game.genres)

                    for genre_game in matching_genre_games:
                        if genre_game not in matching_games['gaming_history']:
                            matching_games['gaming_history'].append(genre_game)
    return matching_games

def apply_filters(favorite_genres, preferred_platforms, matching_games):
    """Apply filters to match games based on user preferences and genres."""

    genre_filters = Q()
    platform_filters = Q()

    for genre in favorite_genres:
        genre_filters |= Q(genres__icontains=genre)

    for platform in preferred_platforms:
        platform_filters |= Q(platforms__icontains=platform)

    common_filters = genre_filters & platform_filters

    platform_exclude_ids = Game.objects.filter(common_filters).values_list('id', flat=True).distinct()

    platform_exclude_filters = Q(id__in=platform_exclude_ids)

    matching_games['favorite_genres'] = Game.objects.filter(genre_filters)
    matching_games['common_genres_platforms'] = Game.objects.filter(common_filters)
    matching_games['preferred_platforms'] = Game.objects.filter(platform_filters).exclude(platform_exclude_filters)

    return matching_games