"""Views for the playstyle_compass app."""


from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from utils.constants import genres, all_platforms
from .models import GamingPreferences, UserPreferences, Game, Review
from .forms import ReviewForm

from .helper_functions.get_recommendations_helpers import (
    initialize_matching_games,
    process_user_data,
    filter_preferences,
    sort_matching_games,
)

from django.core.exceptions import ObjectDoesNotExist


@login_required
def add_review(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user

    existing_review = Review.objects.filter(game=game, user=user).first()

    if existing_review:
        messages.error(request, "You have already reviewed this game.")
        return redirect('playstyle_compass:index.html')  # Not finished !!!

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            profile_name = request.user.userprofile.profile_name

            review = Review(
                game=game,
                user=user,
                reviewers=profile_name,
                review_deck=form.cleaned_data['review_deck'],
                review_description=form.cleaned_data['review_description'],
                score=form.cleaned_data['score']
            )

            review.save()

            messages.success(request, "Your review has been successfully submitted.")
            next_url = request.GET.get('next', reverse('playstyle_compass:index'))

            return HttpResponseRedirect(next_url)

    else:
        form = ReviewForm()

    context = {
        'page_title': "Add Review :: PlayStyle Compass",
        'form': form,
        'game': game,
    }

    return render(request, 'playstyle_compass/add_review.html', context)


def get_game_reviews(request, game_id):
    """View to get the reviews for a game."""
    game_reviews = Review.objects.filter(game_id=game_id)
    reviews_data = []

    for review in game_reviews:

        reviews_data.append({
            'reviewer': review.reviewers,
            'title': review.review_deck,
            'description': review.review_description,
            'score': review.score,
        })

    return JsonResponse({'reviews': reviews_data})

def get_average_score(request, game_id):
    """View to get the average score of a game."""
    game_reviews = Review.objects.filter(game_id=game_id)
    total_score = 0

    for review in game_reviews:
        total_score += int(review.score)

    average_score = total_score / len(game_reviews) if game_reviews else 0
    total_reviews = len(game_reviews)

    return JsonResponse({'average_score': average_score, 'total_reviews': total_reviews})


@login_required
def delete_reviews(request, game_id):
    """View for deleting user reviews."""
    game = get_object_or_404(Game, id=game_id)
    user = request.user

    try:
        review = Review.objects.get(game=game, user=user)
        review.delete()
        messages.success(request, "Your review has been successfully deleted.")
    except Review.DoesNotExist:
        messages.error(request, "You haven't written a review for this game.")

    return redirect('playstyle_compass:favorite_games')


def index(request):
    """Home Page"""
    upcoming_titles = [
        "Little Nightmares III",
        "Reka",
        "Neva",
        "Animal Well",
        "Princess Peach Showtime!",
        "Anger Foot",
        "Earthblade",
        "Vampire: The Masquerade - Bloodlines 2",
    ]
    popular_titles = [
        "Honkai: Star Rail",
        "Diablo IV",
        "Farming Simulator 23",
        "Fortnite",
        "Overwatch",
        "The Witcher 3: Wild Hunt",
        "Baldur's Gate 3",
    ]

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
    user = request.user
    user_preferences = UserPreferences.objects.get(user=user)

    matching_games = initialize_matching_games()
    matching_games = process_user_data(user_preferences, matching_games)
    matching_games = filter_preferences(user_preferences, matching_games)
    matching_games = sort_matching_games(request, matching_games)
    paginated_games = paginate_matching_games(request, matching_games)

    context = {
        "page_title": "Recommendations :: PlayStyle Compass",
        "user_preferences": user_preferences,
        "paginated_games": dict(paginated_games),
    }

    return render(request, "playstyle_compass/recommendations.html", context)


def paginate_matching_games(request, matching_games):
    games_per_page = 10
    paginated_games = defaultdict(list)

    for category, game_list in matching_games.items():
        paginator = Paginator(game_list, games_per_page)
        page_number = request.GET.get(f"{category}_page", 1)

        try:
            page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page = paginator.page(1)

        paginated_games[category] = page

    return paginated_games


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
    """View for toggling a game's favorite status for the current user."""
    if request.method == "POST":
        game_id = request.POST.get("game_id")
        user = request.user
        user_preferences = UserPreferences.objects.get(user=user)

        favorite_games_list = user_preferences.get_favorite_games()

        if int(game_id) in favorite_games_list:
            user_preferences.remove_favorite_game(game_id)
            is_favorite = False
        else:
            user_preferences.add_favorite_game(game_id)
            is_favorite = True

        return JsonResponse({"is_favorite": is_favorite})


@login_required
def favorite_games(request):
    """View for displaying a user's list of favorite games."""
    user = request.user

    try:
        user_preferences = UserPreferences.objects.get(user=user)
        favorite_games_list = user_preferences.get_favorite_games()
    except ObjectDoesNotExist:
        user_preferences = UserPreferences.objects.create(user=user)
        favorite_games_list = []

    games = Game.objects.filter(id__in=favorite_games_list)

    context = {
        "page_title": "Favorites :: PlayStyle Compass",
        "user_preferences": user_preferences,
        "favorite_games": favorite_games_list,
        "games": games,
    }

    return render(request, "playstyle_compass/favorite_games.html", context)


def top_rated_games(request):
    all_games = Game.objects.all()
    games_with_scores = [(game, game.calculate_overall_score()) for game in all_games]
    sorted_games = sorted(games_with_scores, key=lambda x: x[1], reverse=True)
    top_games = [game for game, score in sorted_games if score >= 4.5]

    context = {
    "page_title": "Top Rated Games :: PlayStyle Compass",
    'top_games': top_games,
    }

    return render(request, 'playstyle_compass/top_rated_games.html', context)
