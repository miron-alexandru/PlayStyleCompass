from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse

from .models import GamingPreferences, UserPreferences, Game

from misc.constants import genres, platforms
from .helper_functions.get_recommendations_helpers import process_gaming_history, apply_filters

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
    """Retrieves personalized game recommendations based
    on user preferences and gaming history."""
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

    # Process gaming history to find matching games
    matching_games = process_gaming_history(gaming_history, unique_games, unique_genres, matching_games)

    # Apply genre and platform filters
    matching_games = apply_filters(favorite_genres, preferred_platforms, matching_games)

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