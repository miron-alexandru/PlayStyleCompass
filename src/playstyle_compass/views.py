"""Views for the playstyle_compass app."""


from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from utils.constants import genres, all_platforms
from .models import GamingPreferences, UserPreferences, Game

from .helper_functions.get_recommendations_helpers import (
    process_gaming_history,
    apply_filters,
)

def index(request):
    """Home Page"""
    upcoming_titles = ["Little Nightmares III", "Reka", "Neva", "Animal Well",
     "Princess Peach Showtime!", "Anger Foot", "Earthblade", "Vampire: The Masquerade - Bloodlines 2"]
    popular_titles = ["Honkai: Star Rail", "Diablo IV", "Farming Simulator 23", "FIFA 14", "Overwatch",
     "The Witcher 3: Wild Hunt", "Baldur's Gate 3"]

    upcoming_games = Game.objects.filter(title__in=upcoming_titles)
    popular_games = Game.objects.filter(title__in=popular_titles)

    context = {
        "upcoming_games": upcoming_games,
        "popular_games": popular_games,
        "page_title": "Index :: PlayStyle Compass",
    }

    return render(request, "playstyle_compass/index.html", context)


@login_required
def gaming_preferences(request):
    """Display and manage a user's gaming preferences."""
    preferences = GamingPreferences.objects.filter(owner=request.user).order_by(
        "date_added"
    )

    context = {
        "page_title": "Define PlayStyle :: PlayStyle Compass",
        "gaming_preferences": preferences,
        "genres": genres,
        "platforms": all_platforms,
    }

    return render(request, "playstyle_compass/gaming_preferences.html", context)


@login_required
def update_preferences(request):
    """Update user preferences."""
    user = request.user
    try:
        user_preferences = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:
        user_preferences = None

    if request.method == "POST":
        # Process the form submission and update the user's preferences
        gaming_history = request.POST.get("gaming_history")
        favorite_genres = request.POST.getlist("favorite_genres")
        platforms = request.POST.getlist("platforms")

        # Update the user's preferences in the database
        user_preferences, created = UserPreferences.objects.get_or_create(user=user)
        user_preferences.gaming_history = gaming_history
        user_preferences.favorite_genres = ", ".join(favorite_genres)
        user_preferences.platforms = ", ".join(platforms)
        user_preferences.save()

    context = {
        "page_title": "Your PlayStyle :: PlayStyle Compass",
        "user_preferences": user_preferences,
        "genres": genres,
        "platforms": all_platforms,
    }

    return render(request, "playstyle_compass/update_preferences.html", context)


@login_required
def save_gaming_history(request):
    """Save gaming history for the user."""
    if request.method == "POST":
        new_gaming_history = request.POST.get("gaming_history")
        user_preferences = UserPreferences.objects.get(user=request.user)
        user_preferences.gaming_history = new_gaming_history
        user_preferences.save()
    return redirect("playstyle_compass:update_preferences")


@login_required
def save_favorite_genres(request):
    """Save favorite genres for the user."""
    if request.method == "POST":
        new_favorite_genres = request.POST.getlist("favorite_genres")
        user_preferences = UserPreferences.objects.get(user=request.user)
        user_preferences.favorite_genres = ", ".join(new_favorite_genres)
        user_preferences.save()

    return redirect("playstyle_compass:update_preferences")


@login_required
def save_platforms(request):
    """Save platforms for the user."""
    if request.method == "POST":
        new_platforms = request.POST.getlist("platforms")
        user_preferences = UserPreferences.objects.get(user=request.user)
        user_preferences.platforms = ", ".join(new_platforms)
        user_preferences.save()

    return redirect("playstyle_compass:update_preferences")

@login_required
def clear_preferences(request):
    """Resets the user's gaming preferences."""
    user = request.user
    try:
        user_preferences = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:
        user_preferences = None

    if user_preferences:
        user_preferences.gaming_history = ""
        user_preferences.favorite_genres = ""
        user_preferences.platforms = ""
        user_preferences.save()

    return redirect("playstyle_compass:update_preferences")


@login_required
def get_recommendations(request):
    """Retrieves personalized game recommendations based on user preferences and gaming history."""
    user = request.user
    user_preferences = UserPreferences.objects.get(user=user)

    # Extract user preferences and gaming history
    favorite_genres = [
        genre.strip() for genre in user_preferences.favorite_genres.split(",")
    ]
    preferred_platforms = [
        platform.strip() for platform in user_preferences.platforms.split(",")
    ]
    gaming_history = [
        game.strip() for game in user_preferences.gaming_history.split(",")
    ]

    # Initialize matching_games dictionary
    matching_games = {
        "gaming_history": [],
        "favorite_genres": [],
        "common_genres_platforms": [],
        "preferred_platforms": [],
    }

    # Process gaming history and apply filters
    unique_games = set()
    unique_genres = set()

    matching_games = process_gaming_history(
        gaming_history, unique_games, unique_genres, matching_games
    )
    matching_games = apply_filters(favorite_genres, preferred_platforms, matching_games)

    # Pagination setup
    games_per_page = 15
    paginated_games = defaultdict(list)

    for category, game_list in matching_games.items():
        paginator = Paginator(game_list, games_per_page)
        page_number = request.GET.get(f"{category}_page", 1)

        try:
            page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page = paginator.page(1)

        paginated_games[category] = page

    context = {
        "page_title": "Recommendations :: PlayStyle Compass",
        "user_preferences": user_preferences,
        "paginated_games": dict(paginated_games),
    }

    return render(request, "playstyle_compass/recommendations.html", context)


def search_results(request):
    """Retrieves games from the database that match a given
    search query and renders a search results page.
    """
    query = request.GET.get("query")
    games = Game.objects.filter(title__icontains=query)

    context = {
        "page_title": "Serach Results :: PlayStyle Compass",
        "query": query,
        "games": games,
    }

    return render(request, "playstyle_compass/search_results.html", context)


def autocomplete_view(request):
    """Provides autocomplete suggestions for game titles based on a user's query."""
    query = request.GET.get("query", "")
    results = []

    if query:
        games = Game.objects.filter(title__icontains=query)
        results = list(games.values("title"))

    return JsonResponse(results, safe=False)

@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        user = request.user
        user_preferences = UserPreferences.objects.get(user=user)

        # Get the list of favorite games as a list of game IDs
        favorite_games_list = user_preferences.get_favorite_games()

        if int(game_id) in favorite_games_list:
            user_preferences.remove_favorite_game(game_id)
            is_favorite = False
        else:
            user_preferences.add_favorite_game(game_id)
            is_favorite = True

        return JsonResponse({'is_favorite': is_favorite})

@login_required
def favorite_games(request):
    user = request.user
    user_preferences = UserPreferences.objects.get(user=user)
    favorite_games_list = user_preferences.get_favorite_games()

    games = Game.objects.filter(id__in=favorite_games_list)
    
    context = {
        'user_preferences': user_preferences,
        'favorite_games': favorite_games_list,
        'games': games,
    }

    return render(request, 'playstyle_compass/favorite_games.html', context)