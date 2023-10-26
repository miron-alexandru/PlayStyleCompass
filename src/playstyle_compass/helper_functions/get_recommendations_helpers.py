"""
The 'get_recommendations_helpers' module contains helper functions used for
the get_recommendations view function."""

import re

from django.db.models import Q
from ..models import Game
from datetime import date, datetime


def find_matching_title_games(history_game):
    pattern = re.escape(history_game).replace(r"\ ", r".*?")
    pattern = f".*{pattern}.*"
    return Game.objects.filter(title__iregex=rf"^{pattern}")


def find_matching_genre_games(matching_game):
    if matching_game.genres:
        return Game.objects.filter(genres__icontains=matching_game.genres)
    return []


def process_gaming_history(gaming_history, unique_games, unique_genres, matching_games):
    current_date = date.today()

    games_to_exclude = []

    for history_game in gaming_history:
        matching_title_games = find_matching_title_games(history_game)

        for matching_game in matching_title_games:
            if matching_game not in unique_games:
                unique_games.add(matching_game)
                unique_genres.add(matching_game.genres)

                matching_genre_games = find_matching_genre_games(matching_game)

                for genre_game in matching_genre_games:
                    if genre_game not in matching_games["gaming_history"]:
                        matching_games["gaming_history"].append(genre_game)

                    try:
                        release_date = datetime.strptime(
                            genre_game.release_date, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        release_date = datetime.strptime(
                            genre_game.release_date + "-01-01", "%Y-%m-%d"
                        ).date()

                    if release_date >= current_date:
                        games_to_exclude.append(genre_game)

    matching_games["gaming_history"] = [
        game
        for game in matching_games["gaming_history"]
        if game not in games_to_exclude
    ]

    return matching_games


def apply_filters(favorite_genres, preferred_platforms, matching_games):
    """Apply filters to match games based on user preferences and genres."""
    current_date = date.today()
    genre_filters = Q()
    platform_filters = Q()

    for genre in favorite_genres:
        genre_filters |= Q(genres__icontains=genre)

    for platform in preferred_platforms:
        platform_filters |= Q(platforms__icontains=platform)

    common_filters = genre_filters & platform_filters

    exclude_upcoming = Q(release_date__gte=current_date)

    matching_games["favorite_genres"] = Game.objects.filter(genre_filters).exclude(
        exclude_upcoming
    )
    matching_games["common_genres_platforms"] = Game.objects.filter(
        common_filters
    ).exclude(exclude_upcoming)
    matching_games["preferred_platforms"] = Game.objects.filter(
        platform_filters
    ).exclude(exclude_upcoming)
    matching_games["upcoming_games"] = Game.objects.filter(exclude_upcoming)

    return matching_games


def initialize_matching_games():
    """Initialize an empty dictionary for storing matching games in various categories."""
    return {
        "gaming_history": [],
        "favorite_genres": [],
        "common_genres_platforms": [],
        "preferred_platforms": [],
        "upcoming_games": [],
    }


def process_user_data(user_preferences, matching_games):
    """Process user preferences and gaming history to find matching games."""
    favorite_genres = [
        genre.strip() for genre in user_preferences.favorite_genres.split(",")
    ]
    preferred_platforms = [
        platform.strip() for platform in user_preferences.platforms.split(",")
    ]
    gaming_history = [
        game.strip() for game in user_preferences.gaming_history.split(",")
    ]

    unique_games = set()
    unique_genres = set()

    matching_games = process_gaming_history(
        gaming_history, unique_games, unique_genres, matching_games
    )

    return matching_games


def filter_preferences(user_preferences, matching_games):
    """Filter matching games based on user's favorite genres and preferred platforms."""
    favorite_genres = [
        genre.strip() for genre in user_preferences.favorite_genres.split(",")
    ]
    preferred_platforms = [
        platform.strip() for platform in user_preferences.platforms.split(",")
    ]

    return apply_filters(favorite_genres, preferred_platforms, matching_games)


def sort_matching_games(request, matching_games):
    """Sort matching games based on the user's chosen sorting option."""
    sort_option = request.GET.get("sort", "recommended")
    sorting_functions = {
        "release_date_asc": lambda game: game.release_date,
        "release_date_desc": lambda game: game.release_date,
        "recommended": None,
    }

    sort_key_function = sorting_functions.get(sort_option)
    if sort_key_function:
        for category, game_list in matching_games.items():
            matching_games[category] = sorted(game_list, key=sort_key_function)
            if sort_option == "release_date_desc":
                matching_games[category] = list(reversed(matching_games[category]))

    return matching_games
