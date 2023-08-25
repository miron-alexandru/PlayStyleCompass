from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.db.models import Q

from .models import GamingPreferences, UserPreferences, Game
from misc.constants import genres, platforms


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
    # Get the currently logged-in user
    user = request.user
    
    # Fetch the user's preferences from the database
    user_preferences = UserPreferences.objects.get(user=user)

    # Extract and clean up user preferences from strings
    favorite_genres = [genre.strip() for genre in user_preferences.favorite_genres.split(',')]
    preferred_platforms = [platform.strip() for platform in user_preferences.platforms.split(',')]
    gaming_history = [game.strip() for game in user_preferences.gaming_history.split(',')]

    # Create filters for genres, platforms, and history
    genre_filters = Q()
    platform_filters = Q()
    history_filters = Q()

    # Build filters for each favorite genre
    for genre in favorite_genres:
        genre_filters |= Q(genres__icontains=genre)

    # Build filters for each preferred platform
    for platform in preferred_platforms:
        platform_filters |= Q(platforms__icontains=platform)

    # Build filters for each game in gaming history
    for history_game in gaming_history:
        history_filters |= Q(title__icontains=history_game)

    # Get matching games based on different filters
    matching_games = {
        'gaming_history': Game.objects.filter(history_filters),
        'favorite_genres': Game.objects.filter(genre_filters),
    }

    # Create filters for common genres and platforms
    common_filters = genre_filters & platform_filters
    matching_games['common_genres_platforms'] = Game.objects.filter(common_filters)

    # Identify game IDs to be excluded from preferred platforms
    platform_exclude_ids = Game.objects.filter(common_filters).values_list('id', flat=True).distinct()

    # Create filters to exclude common games from preferred platforms
    platform_exclude_filters = Q()
    for game_id in platform_exclude_ids:
        platform_exclude_filters |= Q(id=game_id)

    # Filter preferred platforms based on exclusion
    preferred_platform_filters = platform_filters & ~platform_exclude_filters
    matching_games['preferred_platforms'] = Game.objects.filter(preferred_platform_filters)

    # Prepare context for rendering
    context = {
        'user_preferences': user_preferences,
        'matching_games': matching_games,
    }

    # Render the recommendations page with the prepared context
    return render(request, 'playstyle_compass/recommendations.html', context)

def search_results(request):
    query = request.GET.get('query')
    games = Game.objects.filter(title__icontains=query)
    context = {'query': query, 'games': games}
    return render(request, 'playstyle_compass/search_results.html', context)

def autocomplete_view(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        games = Game.objects.filter(title__icontains=query)
        results = list(games.values('title'))

    return JsonResponse(results, safe=False)