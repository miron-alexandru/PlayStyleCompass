"""Views for the playstyle_compass app."""

from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Q

from utils.constants import genres, all_platforms
from .models import UserPreferences, Game, Review, SharedGame, Franchise, Character
from .forms import ReviewForm
from users.models import Notification

from .helper_functions.views_helpers import (
    RecommendationEngine,
    calculate_game_scores,
    calculate_single_game_score,
    paginate_matching_games_query,
    paginate_matching_games_dict,
    paginate_objects,
    get_friend_list,
    calculate_average_similarity,
)

from django.utils.translation import gettext as _


def index(request):
    """View for Home Page"""
    upcoming_titles = [
        "Little Nightmares III",
        "Reka",
        "Obscurity: Unknown Threat",
        "Princess Peach Showtime!",
        "Earthblade",
        "Vampire: The Masquerade - Bloodlines 2",
        "Anger Foot",
        "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
        "Wuchang: Fallen Feathers",
        "Zenless Zone Zero",
    ]
    popular_titles = [
        "Honkai: Star Rail",
        "Diablo IV",
        "Fortnite",
        "Overwatch",
        "The Witcher 3: Wild Hunt",
        "Baldur's Gate 3",
        "League of Legends",
        "Hogwarts Legacy",
        "NieR:Automata",
        "Palworld",
    ]

    popular_franchise_titles = [
        "Assassin's Creed",
        "Tomb Raider",
        "Grand Theft Auto",
        "Mortal Kombat",
        "Halo",
        "Battlefiled",
        "God of War",
        "The Witcher",
        "The Sims",
        "Final Fantasy",
        "FIFA",
    ]

    upcoming_games = Game.objects.filter(title__in=upcoming_titles)
    popular_games = Game.objects.filter(title__in=popular_titles)
    popular_franchises = Franchise.objects.filter(title__in=popular_franchise_titles)

    context = {
        "page_title": _("Home :: PlayStyle Compass"),
        "upcoming_games": upcoming_games,
        "popular_games": popular_games,
        "popular_franchises": popular_franchises,
        "search_bar_type": "search_games",
    }

    return render(request, "base/index.html", context)


@login_required
def gaming_preferences(request):
    """Display and manage a user's gaming preferences."""
    context = {
        "page_title": _("Define PlayStyle :: PlayStyle Compass"),
        "genres": genres,
        "platforms": all_platforms,
    }

    return render(request, "preferences/create_gaming_preferences.html", context)


@login_required
def update_preferences(request):
    """Update user preferences."""
    user = request.user
    user_preferences, created = UserPreferences.objects.get_or_create(user=user)

    if request.method == "POST":
        gaming_history = request.POST.get("gaming_history")
        favorite_genres = request.POST.getlist("favorite_genres")
        platforms = request.POST.getlist("platforms")

        user_preferences.gaming_history = gaming_history
        user_preferences.favorite_genres = ", ".join(favorite_genres)
        user_preferences.platforms = ", ".join(platforms)

        user_preferences.save()

    context = {
        "page_title": _("Your PlayStyle :: PlayStyle Compass"),
        "user_preferences": user_preferences,
        "genres": genres,
        "platforms": all_platforms,
    }

    return render(request, "preferences/update_gaming_preferences.html", context)


@login_required
def save_gaming_history(request):
    """Save gaming history for the user."""
    return _save_user_preference(
        request, "gaming_history", "playstyle_compass:update_preferences"
    )


@login_required
def save_favorite_genres(request):
    """Save favorite genres for the user."""
    return _save_user_preference(
        request, "favorite_genres", "playstyle_compass:update_preferences"
    )


@login_required
def save_platforms(request):
    """Save platforms for the user."""
    return _save_user_preference(
        request, "platforms", "playstyle_compass:update_preferences"
    )


def _save_user_preference(request, field_name, redirect_view):
    """Common function to save user preferences."""
    if request.method == "POST":
        new_values = request.POST.getlist(field_name)
        user_preferences = UserPreferences.objects.get(user=request.user)
        setattr(user_preferences, field_name, ", ".join(new_values))
        user_preferences.save()

    return redirect(redirect_view)


@login_required
def clear_preferences(request):
    """Resets the user's gaming preferences."""
    user = request.user
    user_preferences, created = UserPreferences.objects.get_or_create(user=user)

    if user_preferences:
        user_preferences.gaming_history = ""
        user_preferences.favorite_genres = ""
        user_preferences.platforms = ""
        user_preferences.save()

    return redirect("playstyle_compass:update_preferences")


@login_required
def get_recommendations(request):
    """View to get game recommendations based on user preferences."""
    user = request.user
    user_preferences = UserPreferences.objects.get(user=user)

    if user_preferences.gaming_history == "" or user_preferences.favorite_genres == "":
        return redirect("playstyle_compass:update_preferences")

    recommendation_engine = RecommendationEngine(request, user_preferences)
    recommendation_engine.process()

    matching_games = recommendation_engine.matching_games
    paginated_games = paginate_matching_games_dict(request, matching_games)

    user_friends = get_friend_list(user)

    context = {
        "page_title": _("Recommendations :: PlayStyle Compass"),
        "user_preferences": user_preferences,
        "paginated_games": dict(paginated_games),
        "user_friends": user_friends,
    }

    return render(request, "games/recommendations.html", context)


def search_results(request):
    """Retrieves games from the database that match a given
    search query and renders a search results page.
    """
    user_preferences = (
        UserPreferences.objects.get_or_create(user=request.user)[0]
        if request.user.is_authenticated
        else None
    )

    query = request.GET.get("query")

    if query and len(query) < 2:
        return HttpResponseBadRequest("Invalid query. Please enter at least 2 characters.")

    games = Game.objects.filter(title__icontains=query)

    games = calculate_game_scores(games)
    games = paginate_matching_games_query(request, games)

    user_friends = get_friend_list(request.user) if request.user.is_authenticated else None

    context = {
        "page_title": _("Search Results :: PlayStyle Compass"),
        "query": query,
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "search_bar_type": "search_games",
    }

    return render(request, "games/search_games.html", context)

def search_franchises(request):
    """Retrieves franchises from the database that match a given
    search query and renders a search results page.
    """
    query = request.GET.get("query")
    if query and len(query) < 2:
        return HttpResponseBadRequest("Invalid query. Please enter at least 2 characters.")

    franchises = Franchise.objects.filter(title__icontains=query)
    franchises = paginate_objects(request, franchises)

    context = {
        "page_title": _("Search Results :: PlayStyle Compass"),
        "query": query,
        "franchises": franchises,
        "search_bar_type": "search_franchises",
    }

    return render(request, "franchises/search_franchises.html", context)


def autocomplete_games(request):
    """Provides autocomplete suggestions for games based on a user's query."""
    query = request.GET.get("query", "")
    results = []

    if query:
        games = Game.objects.filter(title__icontains=query)
        results = list(games.values("title"))

    return JsonResponse(results, safe=False)


def autocomplete_franchises(request):
    """Provides autocomplete suggestions for franchises based on a user's query."""
    query = request.GET.get("query", "")
    results = []

    if query:
        franchises = Franchise.objects.filter(title__icontains=query)
        results = list(franchises.values("title"))

    return JsonResponse(results, safe=False)


@login_required
def toggle_favorite(request):
    """View for toggling a game's favorite status for the current user."""
    if request.method == "POST":
        game_id = request.POST.get("game_id")
        user = request.user
        user_preferences = UserPreferences.objects.get(user=user)

        favorite_games_list = user_preferences.get_favorite_games()

        # Check if the game is already in the favorites and make the necessary changes
        if int(game_id) in favorite_games_list:
            user_preferences.remove_favorite_game(game_id)
            is_favorite = False
        else:
            user_preferences.add_favorite_game(game_id)
            is_favorite = True

        return JsonResponse({"is_favorite": is_favorite})


@login_required
def toggle_game_queue(request):
    """View for toggling a game's queued status for the current user."""
    if request.method == "POST":
        game_id = request.POST.get("game_id")
        user = request.user
        user_preferences = UserPreferences.objects.get(user=user)

        game_queue = user_preferences.get_game_queue()

        # Check if the game is already in the queue and make the necessary changes
        if int(game_id) in game_queue:
            user_preferences.remove_game_from_queue(game_id)
            in_queue = False
        else:
            user_preferences.add_game_to_queue(game_id)
            in_queue = True

        return JsonResponse({"in_queue": in_queue})


@login_required
def user_reviews(request, user_id=None):
    """View to get the user reviews."""
    # Determine the user based on the provided user_id or the authenticated user
    user = request.user if user_id is None else get_object_or_404(User, id=user_id)

    other_user_profile = user != request.user
    user_preferences, created = UserPreferences.objects.get_or_create(user=user)

    # Check permissions for viewing user reviews in other user profiles
    if other_user_profile:
        if not user_preferences.show_reviews:
            messages.error(
                request, _("You don't have permission to view this content.")
            )
            return redirect("playstyle_compass:index")

    user_reviews = Review.objects.filter(user=user)
    user_games = calculate_game_scores([review.game for review in user_reviews])
    current_viewer_preferences, created = UserPreferences.objects.get_or_create(
        user=request.user
    )

    user_friends = get_friend_list(request.user)

    context = {
        "page_title": _("Games Reviewed :: PlayStyle Compass"),
        "games": user_games,
        "user_preferences": user_preferences,
        "other_user": other_user_profile,
        "user_name": user.userprofile.profile_name,
        "current_viewer_preferences": current_viewer_preferences,
        "user_friends": user_friends,
    }

    return render(request, "reviews/user_reviews.html", context)


@login_required
def favorite_games(request, user_id=None):
    """View for the favorite games."""
    return _get_games_view(
        request,
        _("Favorites :: PlayStyle Compass"),
        "favorite_games",
        "games/favorite_games.html",
        user_id=user_id,
    )


@login_required
def game_queue(request, user_id=None):
    """View for the games queue."""
    return _get_games_view(
        request,
        _("Game Queue :: PlayStyle Compass"),
        "game_queue",
        "games/game_queue.html",
        user_id=user_id,
    )


def _get_games_view(request, page_title, list_name, template_name, user_id=None):
    """
    Helper view function to get games in a similar way for different pages.

    Args:
    - request: The Django request object.
    - page_title: The title of the page.
    - list_name: The name of the game list (e.g., "favorite_games", "game_queue").
    - template_name: The name of the template to render.
    - user_id: The ID of the user whose games are being viewed (default is None, which means the authenticated user).
    """

    # Determine the user based on the provided user_id or the authenticated user
    user = request.user if user_id is None else get_object_or_404(User, id=user_id)

    # Check if the viewed profile is not the current user's profile
    other_user_profile = user != request.user

    # Get or create the UserPreferences object for the specified user
    user_preferences, created = UserPreferences.objects.get_or_create(user=user)

    # Check permissions for viewing certain content in other user profiles
    if other_user_profile:
        if not user_preferences.show_favorites and list_name == "favorite_games":
            messages.error(
                request, _("You don't have permission to view this content.")
            )
            return redirect("playstyle_compass:index")

        if not user_preferences.show_in_queue and list_name == "game_queue":
            messages.error(
                request, _("You don't have permission to view this content.")
            )
            return redirect("playstyle_compass:index")

    # Get the list of game IDs based on the specified list_name and user_preferences
    game_list = getattr(user_preferences, f"get_{list_name}")() if not created else []

    games = calculate_game_scores(Game.objects.filter(id__in=game_list))

    current_viewer_preferences, created = UserPreferences.objects.get_or_create(
        user=request.user
    )

    user_friends = get_friend_list(request.user)

    context = {
        "page_title": page_title,
        "user_preferences": user_preferences,
        list_name: game_list,
        "games": games,
        "other_user": other_user_profile,
        "user_name": user.userprofile.profile_name,
        "current_viewer_preferences": current_viewer_preferences,
        "user_friends": user_friends,
    }

    return render(request, template_name, context)


def top_rated_games(request):
    """View to display top rated games."""
    user = request.user if request.user.is_authenticated else None
    user_preferences = UserPreferences.objects.get(user=user) if user else None

    top_games = Game.objects.annotate(average_score=Avg("review__score")).filter(
        average_score__gt=4
    )

    top_games = calculate_game_scores(top_games)
    user_friends = get_friend_list(user) if user else []

    context = {
        "page_title": _("Top Rated Games :: PlayStyle Compass"),
        "games": top_games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
    }

    return render(request, "games/top_rated_games.html", context)


def upcoming_games(request):
    """View the upcoming games."""
    user = request.user if request.user.is_authenticated else None
    user_preferences = UserPreferences.objects.get(user=user) if user else None
    current_date = date.today()

    upcoming_filter = (
        Q(release_date__gte=current_date) |
        Q(release_date__regex=r'^\d{4}$', release_date__gte=str(current_date.year))
    )

    upcoming_games = calculate_game_scores(Game.objects.filter(upcoming_filter))
    paginated_games = paginate_matching_games_query(request, upcoming_games)
    user_friends = get_friend_list(user) if user else []

    context = {
        "page_title": _("Upcoming Games :: PlayStyle Compass"),
        "upcoming_games": paginated_games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
    }

    return render(request, "games/upcoming_games.html", context)

@login_required
def add_review(request, game_id):
    """View to add a review for a game."""
    game = get_object_or_404(Game, pk=game_id)
    user = request.user

    existing_review = Review.objects.filter(game=game, user=user).first()

    if existing_review:
        messages.error(request, _("You have already reviewed this game!"))
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", reverse("playstyle_compass:index"))
        )

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            profile_name = request.user.userprofile.profile_name

            review_data = {
                "game": game,
                "user": user,
                "reviewers": profile_name,
                "review_deck": form.cleaned_data["review_deck"],
                "review_description": form.cleaned_data["review_description"],
                "score": form.cleaned_data["score"],
            }

            Review.objects.create(**review_data)

            messages.success(request, _("Your review has been successfully submitted."))
            return HttpResponseRedirect(
                request.GET.get("next", reverse("playstyle_compass:index"))
            )

    else:
        form = ReviewForm()

    context = {
        "page_title": _("Add Review :: PlayStyle Compass"),
        "form": form,
        "game": game,
    }

    return render(request, "reviews/add_review.html", context)


@login_required
def edit_review(request, game_id):
    """View to edit reviews for games."""
    game = get_object_or_404(Game, id=game_id)
    user = request.user
    next_url = request.GET.get("next", reverse("playstyle_compass:index"))

    try:
        # Attempt to retrieve the user's existing review for the specified game
        review = Review.objects.get(game=game, user=user)
    except Review.DoesNotExist:
        # Handle the case where the user hasn't written any reviews for this game
        messages.error(request, _("You haven't written any reviews for this game!"))
        return HttpResponseRedirect(next_url)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your review has been successfully updated."))
            return HttpResponseRedirect(next_url)
    else:
        form = ReviewForm(instance=review)

    context = {
        "page_title": _("Edit Review :: PlayStyle Compass"),
        "form": form,
        "game": game,
    }

    return render(request, "reviews/edit_review.html", context)


def get_game_reviews(request, game_id):
    """View to get the reviews for a game."""
    game_reviews = Review.objects.filter(game_id=game_id)
    invalid_user_id = "invalid_user"

    reviews_data = [
        {
            "id": review.id,
            "reviewer": review.reviewers,
            "title": review.review_deck,
            "description": review.review_description,
            "score": review.score,
            "likes": review.likes,
            "dislikes": review.dislikes,
            "user_id": invalid_user_id
            if "-" in str(review.user_id)
            else review.user_id,
        }
        for review in game_reviews
    ]

    return JsonResponse({"reviews": reviews_data})


def like_review(request):
    if request.method == "POST" and request.user.is_authenticated:
        review_id = request.POST.get("review_id")
        user_id = request.user.id

        if review_id:
            review = get_object_or_404(Review, id=review_id)

            if review.user_id == user_id:
                return JsonResponse({"message": _("You cannot like your own review.")})

            if "-" in str(review.user_id):
                review.user_id = -1

            if review.user_has_disliked(user_id):
                review.remove_dislike(user_id)

            if review.user_has_liked(user_id):
                review.remove_like(user_id)
            else:
                review.add_like(user_id)

            return JsonResponse(
                {"likes": review.likes, "dislikes": review.dislikes, "message": ""}
            )

        return JsonResponse({"error": _("Review ID invalid.")})

    return JsonResponse(
        {"message": _("You must be logged in to like or dislike a review.")}
    )


def dislike_review(request):
    if request.method == "POST" and request.user.is_authenticated:
        review_id = request.POST.get("review_id")
        user_id = request.user.id

        if review_id:
            review = get_object_or_404(Review, id=review_id)

            if review.user_id == user_id:
                return JsonResponse(
                    {"message": _("You cannot dislike your own review.")}
                )

            if "-" in str(review.user_id):
                review.user_id = -1

            if review.user_has_liked(user_id):
                review.remove_like(user_id)

            if review.user_has_disliked(user_id):
                review.remove_dislike(user_id)
            else:
                review.add_dislike(user_id)

            return JsonResponse(
                {"dislikes": review.dislikes, "likes": review.likes, "message": ""}
            )

        return JsonResponse({"error": _("Review ID invalid.")})

    return JsonResponse(
        {"message": _("You must be logged in to like or dislike a review.")}
    )


@login_required
def delete_reviews(request, game_id):
    """View for deleting user reviews."""
    game = get_object_or_404(Game, id=game_id)
    user = request.user
    next_url = request.GET.get("next", reverse("playstyle_compass:index"))

    try:
        review = Review.objects.get(game=game, user=user)
        review.delete()
        messages.success(request, _("Your review has been successfully deleted!"))
    except Review.DoesNotExist:
        messages.error(request, _("You haven't written any reviews for this game!"))

    return HttpResponseRedirect(next_url)


def view_game(request, game_id):
    """View used to display a single game."""
    user = request.user if request.user.is_authenticated else None
    user_preferences = UserPreferences.objects.get(user=user) if user else None

    game = get_object_or_404(Game, id=game_id)
    game = calculate_single_game_score(game)

    user_friends = get_friend_list(user) if user else []

    context = {
        "page_title": f"{game.title} :: PlayStyle Compass",
        "game": game,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
    }

    return render(request, "games/view_game.html", context)


@login_required
def share_game(request, game_id):
    """View used to share a game with another user."""

    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")

        # Check if receiver_id is provided
        if receiver_id is not None:
            # Get the Game and User objects
            game = get_object_or_404(Game, id=game_id)
            receiver = get_object_or_404(User, id=receiver_id)

            # Check if the game is already shared with the receiver
            if SharedGame.objects.filter(
                sender=request.user, receiver=receiver, game_id=game.id
            ).exists():
                return JsonResponse(
                    {
                        "status": "error",
                        "message": _(
                            "You have already shared %(game_title)s with %(profile_name)s."
                        )
                        % {
                            "game_title": game.title,
                            "profile_name": receiver.userprofile.profile_name,
                        },
                    }
                )

            # Create the message content with information about the shared game
            message_content = f"""
                <p><strong>Hello {receiver.userprofile.profile_name}!</strong></p>
                <p>I just wanted to share this awesome game named <strong>{game.title}</strong> with you.</p>
                <div class="game-message">
                    <p>Check it out <a href='{reverse('playstyle_compass:view_game', args=[game.id])}' target='_blank'>here</a>!</p>
                </div>
            """

            # Create a new Message object
            message = SharedGame.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_content,
                game_id=game.id,
            )

            user_in_notification = request.user.userprofile.profile_name
            profile_url = reverse("users:view_profile", args=[user_in_notification])
            navigation_url = reverse("playstyle_compass:games_shared")

            message = f"""<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a>
                just shared a game with you!<br> 
                <a class="notification-link" title="Navigate" href="{navigation_url}">Navigate to shared games</a>
                """

            notification = Notification(user=receiver, message=message)
            notification.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": _(
                        "You have successfully shared %(game_title)s with %(profile_name)s."
                    )
                    % {
                        "game_title": game.title,
                        "profile_name": receiver.userprofile.profile_name,
                    },
                }
            )

        else:
            return JsonResponse(
                {"status": "error", "message": _("Receiver ID not provided")}
            )

    return JsonResponse({"status": "error", "message": _("Invalid request method")})


@login_required
def view_games_shared(request):
    """View used to display games shared between users."""
    sort_order = request.GET.get("sort_order", None)
    games_received = SharedGame.objects.filter(
        receiver=request.user, is_deleted_by_receiver=False
    )
    games_shared = SharedGame.objects.filter(
        sender=request.user, is_deleted_by_sender=False
    )

    # Sort the shared games based on the selected sort order
    if sort_order == "asc":
        games_received = games_received.order_by("timestamp")
        games_shared = games_shared.order_by("timestamp")
    else:
        games_received = games_received.order_by("-timestamp")
        games_shared = games_shared.order_by("-timestamp")

    context = {
        "page_title": _("Shared Games :: PlayStyle Compass"),
        "games_received": games_received,
        "games_shared": games_shared,
        "selected_sort_order": sort_order,
    }

    return render(request, "games/games_shared.html", context)


@login_required
def delete_shared_games(request):
    """View used to delete selected shared games."""

    if request.method == "POST":
        # Get the list of received games and shared games
        received_games_to_delete = request.POST.getlist("received_games[]")
        shared_games_to_delete = request.POST.getlist("shared_games[]")

        # Update the 'is_deleted_by_receiver' and 'is_deketed_by_sender'
        # fields for received games and shared games
        SharedGame.objects.filter(
            id__in=received_games_to_delete, receiver=request.user
        ).update(is_deleted_by_receiver=True)

        SharedGame.objects.filter(
            id__in=shared_games_to_delete, sender=request.user
        ).update(is_deleted_by_sender=True)

        # Delete messages that meet certain conditions:
        # 1. Both sender and receiver marked as deleted
        # 2. Marked as deleted by receiver and sender is null
        # 3. Marked as deleted by sender and receiver is null
        SharedGame.objects.filter(
            Q(is_deleted_by_receiver=True, is_deleted_by_sender=True)
            | Q(is_deleted_by_receiver=True, sender__isnull=True)
            | Q(is_deleted_by_sender=True, receiver__isnull=True)
        ).delete()

    return redirect("playstyle_compass:games_shared")


@login_required
def similar_playstyles(request):
    """View used to show users with similar playstyles."""
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)

    preferences_to_compare = ["gaming_history", "favorite_genres", "platforms"]
    similarity_threshold = 0.6

    all_user_prefs = UserPreferences.objects.exclude(user=request.user)

    # Find users with similar playstyles based on preferences
    similar_user_playstyles = [
        user
        for user in all_user_prefs
        if calculate_average_similarity(user_preferences, user, preferences_to_compare)
        >= similarity_threshold
    ]

    context = {
        "page_title": _("Similar PlayStyles :: PlayStyle Compass"),
        "similar_user_playstyles": similar_user_playstyles,
        "user_preferences": user_preferences,
    }

    return render(request, "misc/similar_playstyles.html", context)


def view_franchises(request):
    """View used to display all franchises."""
    all_franchises = Franchise.objects.all()

    sort_order = request.GET.get('sort_order', 'default')
    if sort_order == 'asc':
        all_franchises = all_franchises.order_by('title')
    elif sort_order == 'desc':
        all_franchises = all_franchises.order_by('-title')
    elif sort_order == 'games_asc':
        all_franchises = all_franchises.order_by('games_count')
    elif sort_order == 'games_desc':
        all_franchises = all_franchises.order_by('-games_count')

    paginated_franchises = paginate_objects(request, all_franchises)

    context = {
        "page_title": _("Franchises :: PlayStyle Compass"),
        "franchises": paginated_franchises,
        "sort_order": sort_order,
    }

    return render(request, "franchises/franchise_list.html", context)


def franchise(request, franchise_id):
    """View used to display a single franchise."""
    franchise = get_object_or_404(Franchise, id=franchise_id)

    context = {
        "page_title": f"{franchise.title} :: PlayStyle Compass",
        "franchise": franchise,
    }

    return render(request, "franchises/view_franchise.html", context)


def view_characters(request):
    """View used to display all characters."""
    characters = Character.objects.all()

    sort_order = request.GET.get('sort_order', 'default')
    if sort_order == 'asc':
        characters = characters.order_by('name')
    elif sort_order == 'desc':
        characters = characters.order_by('-name')

    paginated_characters = paginate_objects(request, characters)

    context = {
        "page_title": _("Characters :: PlayStyle Compass"),
        "characters": paginated_characters,
        "sort_order": sort_order,
    }

    return render(request, "characters/characters.html", context)

def game_character(request, character_id):
    """View used to display a single character"""
    character = get_object_or_404(Character, id=character_id)

    context = {
        "page_title": f"{character.name} :: PlayStyle Compass",
        "character": character,
    }

    return render(request, "characters/game_character.html", context)


def search_characters(request):
    """Retrieves characters from the database that match a given
    search query and renders a search results page.
    """
    query = request.GET.get("query")
    if query and len(query) < 2:
        return HttpResponseBadRequest("Invalid query. Please enter at least 2 characters.")

    characters = Character.objects.filter(name__icontains=query)
    characters = paginate_objects(request, characters)

    context = {
        "page_title": _("Search Results :: PlayStyle Compass"),
        "query": query,
        "characters": characters,
        "search_bar_type": "search_characters",
    }

    return render(request, "characters/search_characters.html", context)

def autocomplete_characters(request):
    """Provides autocomplete suggestions for characters based on a user's query."""
    query = request.GET.get("query", "")
    results = []

    if query:
        characters = Character.objects.filter(name__icontains=query)
        results = list(characters.values("name"))

    return JsonResponse(results, safe=False)
