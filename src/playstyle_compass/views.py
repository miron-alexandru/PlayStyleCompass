from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.db.models import Q

from .models import GamingPreferences, UserPreferences, Game
from misc.constants import genres, platforms
import re


def index(request):
    """Home Page"""
    return render(request, 'playstyle_compass/index.html')

@login_required
def gaming_preferences(request):
    """Display and manage a user's gaming preferences."""
    preferences = GamingPreferences.objects.filter(owner=request.user).order_by('date_added')

    context = {
    'gaming_preferences': preferences,
    'genres': genres,
    'platforms': platforms,
    }

    return render(request, 'playstyle_compass/gaming_preferences.html', context)

@login_required
def update_preferences(request):
    """Update user preferences."""
    user = request.user
    try:
        user_preferences = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:
        user_preferences = None

    if request.method == 'POST':
        # Process the form submission and update the user's preferences
        gaming_history = request.POST.get('gaming_history')
        favorite_genres = request.POST.getlist('favorite_genres')
        platforms = request.POST.getlist('platforms')

        # Update the user's preferences in the database
        user_preferences, created = UserPreferences.objects.get_or_create(user=user)
        user_preferences.gaming_history = gaming_history
        user_preferences.favorite_genres = ', '.join(favorite_genres)
        user_preferences.platforms = ', '.join(platforms)
        user_preferences.save()

    context = {
        'user_preferences': user_preferences,
    }

    return render(request, 'playstyle_compass/update_preferences.html', context)


@login_required
def get_recommendations(request):
    user = request.user
    user_preferences = UserPreferences.objects.get(user=user)

    favorite_genres = [genre.strip() for genre in user_preferences.favorite_genres.split(',')]
    preferred_platforms = [platform.strip() for platform in user_preferences.platforms.split(',')]
    gaming_history = [game.strip() for game in user_preferences.gaming_history.split(',')]

    matching_games = {
        'gaming_history': [],
        'favorite_genres': [],
        'common_genres_platforms': [],
        'preferred_platforms': [],
    }

    unique_games = set()
    unique_genres = set()

    for history_game in gaming_history:
        if len(history_game) > 3:
            pattern = re.escape(history_game).replace(r'\ ', r'.*?')
            pattern = f'.*{pattern}.*'
            matching_title_games = Game.objects.filter(title__iregex=rf'^{pattern}')
            print(matching_title_games)
            for matching_game in matching_title_games:
                if matching_game not in unique_games:
                    unique_games.add(matching_game)
                    matching_genre_games = Game.objects.filter(genres__icontains=matching_game.genres)
                    for genre_game in matching_genre_games:
                        genre = genre_game.genres
                        if genre not in unique_genres:
                            unique_genres.add(genre)
                            matching_games['gaming_history'].append(genre_game)

    genre_filters = Q()
    platform_filters = Q()

    for genre in favorite_genres:
        genre_filters |= Q(genres__icontains=genre)

    for platform in preferred_platforms:
        platform_filters |= Q(platforms__icontains=platform)

    common_filters = genre_filters & platform_filters
    platform_exclude_ids = Game.objects.filter(common_filters).values_list('id', flat=True).distinct()
    platform_exclude_filters = Q(id__in=platform_exclude_ids)
    preferred_platform_filters = platform_filters & ~platform_exclude_filters

    matching_games['favorite_genres'] = Game.objects.filter(genre_filters)
    matching_games['common_genres_platforms'] = Game.objects.filter(common_filters)
    matching_games['preferred_platforms'] = Game.objects.filter(preferred_platform_filters)

    context = {
        'user_preferences': user_preferences,
        'matching_games': matching_games,
    }

    return render(request, 'playstyle_compass/recommendations.html', context)


def search_results(request):
    """Retrieves games from the database that match a given
    search query and renders a search results page.
    """
    query = request.GET.get('query')
    games = Game.objects.filter(title__icontains=query)
    context = {'query': query, 'games': games}
    return render(request, 'playstyle_compass/search_results.html', context)

def autocomplete_view(request):
    """Provides autocomplete suggestions for game titles based on a user's query."""
    query = request.GET.get('query', '')
    results = []

    if query:
        games = Game.objects.filter(title__icontains=query)
        results = list(games.values('title'))

    return JsonResponse(results, safe=False)