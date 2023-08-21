from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
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
    """Provide game recommendations for the user."""
    user = request.user
    user_preferences = UserPreferences.objects.get(user=user)
    favorite_genres = user_preferences.favorite_genres.split(', ')
    preferred_platforms = user_preferences.platforms.split(', ')
    gaming_history = user_preferences.gaming_history.split(', ')

    genre_filters = Q()
    platform_filters = Q()
    history_filters = Q()

    for genre in favorite_genres:
        genre_filters |= Q(genres__icontains=genre.strip())

    common_filters = genre_filters  # Initialize common filters with genre filters

    for history_game in gaming_history:
        history_filters |= Q(title__icontains=history_game.strip())

    matching_games = {
        'gaming_history': Game.objects.filter(history_filters),
        'favorite_genres': Game.objects.filter(genre_filters),
    }

    # Find games that have common genres and platforms
    common_filters_platforms = Q()
    for platform in preferred_platforms:
        common_filters_platforms |= Q(platforms__icontains=platform.strip())
    
    common_filters &= common_filters_platforms
    matching_games['common_genres_platforms'] = Game.objects.filter(common_filters)

    platform_exclude_ids = (
        Game.objects.filter(common_filters)
        .values_list('id', flat=True)
        .distinct()
    )

    for platform in preferred_platforms:
        platform_filters |= Q(
            Q(platforms__icontains=platform.strip()) & ~Q(id__in=platform_exclude_ids)
        )

    matching_games['preferred_platforms'] = Game.objects.filter(platform_filters)

    context = {
        'user_preferences': user_preferences,
        'matching_games': matching_games,
    }
    return render(request, 'playstyle_compass/recommendations.html', context)
