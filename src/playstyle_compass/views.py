"""Views for the playstyle_compass app."""

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import (
    JsonResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    Http404,
)
from django.urls import reverse
from django.db.models import Avg, Q
from django.utils.translation import gettext as _
from django.utils.html import format_html, escape
from django.utils.timezone import localtime
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from utils.constants import (
    genres,
    all_platforms,
    all_themes,
    connection_type,
    game_style,
)
from users.models import Notification, Follow
from users.misc.helper_functions import create_notification
from .models import (
    UserPreferences,
    Game,
    Review,
    SharedGame,
    Franchise,
    Character,
    GameModes,
    News,
    GameList,
    ListReview,
    ListComment,
    GameStores,
    Poll,
    PollOption,
    Vote,
    Deal,
    SharedDeal,
)
from .forms import (
    ReviewForm,
    GameListForm,
    ListReviewForm,
    PrivacySettingsForm,
    ListCommentForm,
    PollForm,
    VoteForm,
)

from .helper_functions.views_helpers import (
    RecommendationEngine,
    paginate_matching_games,
    paginate_objects,
    get_friend_list,
    calculate_average_similarity,
    gather_game_attributes,
    build_query,
    get_selected_filters,
    sort_game_library,
    get_user_context,
    get_associated_platforms,
    sort_articles,
    get_similar_games,
    get_first_letter,
)


def index(request):
    """View for Home Page"""
    upcoming_titles = [
        "Little Nightmares III",
        "Assassin's Creed Shadows",
        "Astrobotanica",
        "Death Stranding 2: On the Beach",
        "Earthblade",
        "Vampire: The Masquerade - Bloodlines 2",
        "Subnautica 2",
        "Grand Theft Auto VI",
        "Wuchang: Fallen Feathers",
        "The Relic: First Guardian",
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
        "FIFA",
    ]

    upcoming_games = Game.objects.filter(title__in=upcoming_titles)
    popular_games = Game.objects.filter(title__in=popular_titles)
    popular_franchises = Franchise.objects.filter(title__in=popular_franchise_titles)
    articles = News.objects.order_by("-publish_date")[:6]
    top_rated_games = Game.objects.order_by("-average_score")[:10]
    game_deals = Deal.objects.all()[:8]

    context = {
        "page_title": _("Home :: PlayStyle Compass"),
        "upcoming_games": upcoming_games,
        "popular_games": popular_games,
        "popular_franchises": popular_franchises,
        "articles": articles,
        "top_rated_games": top_rated_games,
        "search_bar_type": "search_games",
        "game_deals": game_deals,
    }

    return render(request, "base/index.html", context)


@login_required
def gaming_preferences(request):
    """Display and manage a user's gaming preferences."""
    context = {
        "page_title": _("Define PlayStyle :: PlayStyle Compass"),
        "genres": genres,
        "platforms": all_platforms,
        "themes": all_themes,
        "game_styles": game_style,
        "connection_types": connection_type,
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
        themes = request.POST.getlist("themes")
        platforms = request.POST.getlist("platforms")
        connection_types = request.POST.getlist("connection_types")
        game_styles = request.POST.getlist("game_styles")

        user_preferences.gaming_history = gaming_history
        user_preferences.favorite_genres = ", ".join(favorite_genres)
        user_preferences.themes = ", ".join(themes)
        user_preferences.platforms = ", ".join(platforms)
        user_preferences.connection_types = ", ".join(connection_types)
        user_preferences.game_styles = ", ".join(game_styles)
        user_preferences.save()

    context = {
        "page_title": _("Your PlayStyle :: PlayStyle Compass"),
        "user_preferences": user_preferences,
        "genres": genres,
        "themes": all_themes,
        "platforms": all_platforms,
        "connection_types": connection_type,
        "game_styles": game_style,
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
def save_themes(request):
    """Save themes for user."""
    return _save_user_preference(
        request, "themes", "playstyle_compass:update_preferences"
    )


@login_required
def save_platforms(request):
    """Save platforms for the user."""
    return _save_user_preference(
        request, "platforms", "playstyle_compass:update_preferences"
    )


@login_required
def save_connection_types(request):
    """Save platforms for the user."""
    return _save_user_preference(
        request, "connection_types", "playstyle_compass:update_preferences"
    )


@login_required
def save_game_styles(request):
    """Save platforms for the user."""
    return _save_user_preference(
        request, "game_styles", "playstyle_compass:update_preferences"
    )


def _save_user_preference(request, field_name, redirect_view):
    """Common function to save user preferences."""
    if request.method == "POST":
        new_values = request.POST.getlist(field_name)
        user_preferences = get_object_or_404(UserPreferences, user=request.user)
        setattr(user_preferences, field_name, ", ".join(new_values))
        user_preferences.save()

    return redirect(redirect_view)


@login_required
def save_all_preferences(request):
    """Save all preferences for the user."""
    if request.method == "POST":
        user_preferences = get_object_or_404(UserPreferences, user=request.user)

        user_preferences.gaming_history = ", ".join(
            request.POST.getlist("gaming_history")
        )
        user_preferences.favorite_genres = ", ".join(
            request.POST.getlist("favorite_genres")
        )
        user_preferences.themes = ", ".join(request.POST.getlist("themes"))
        user_preferences.platforms = ", ".join(request.POST.getlist("platforms"))
        user_preferences.connection_types = ", ".join(
            request.POST.getlist("connection_types")
        )
        user_preferences.game_styles = ", ".join(request.POST.getlist("game_styles"))

        user_preferences.save()

    return JsonResponse({"success": True})


@login_required
def clear_preferences(request):
    """Resets the user's gaming preferences."""
    user = request.user
    user_preferences, created = UserPreferences.objects.get_or_create(user=user)

    if user_preferences:
        user_preferences.gaming_history = ""
        user_preferences.favorite_genres = ""
        user_preferences.themes = ""
        user_preferences.platforms = ""
        user_preferences.connection_types = ""
        user_preferences.game_styles = ""
        user_preferences.save()

    return redirect("playstyle_compass:update_preferences")


@login_required
def get_recommendations(request):
    """View to get game recommendations based on user preferences."""
    user = request.user
    user_preferences = get_object_or_404(UserPreferences, user=user)

    if user_preferences.gaming_history == "" or user_preferences.favorite_genres == "":
        return redirect("playstyle_compass:update_preferences")

    recommendation_engine = RecommendationEngine(request, user_preferences)
    recommendation_engine.process()

    matching_games = recommendation_engine.matching_games
    paginated_games = paginate_matching_games(request, matching_games)

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
    user, user_preferences, user_friends = get_user_context(request)

    query = request.GET.get("query")

    if query and len(query) < 2:
        return HttpResponseBadRequest(
            "Invalid query. Please enter at least 2 characters."
        )

    games = Game.objects.filter(title__icontains=query)
    games = paginate_matching_games(request, games)

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
        return HttpResponseBadRequest(
            "Invalid query. Please enter at least 2 characters."
        )

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

    return JsonResponse({"results": results})


def autocomplete_franchises(request):
    """Provides autocomplete suggestions for franchises based on a user's query."""
    query = request.GET.get("query", "")
    results = []

    if query:
        franchises = Franchise.objects.filter(title__icontains=query)
        results = list(franchises.values("title"))

    return JsonResponse({"results": results})


@login_required
def toggle_favorite(request):
    """View for toggling a game's favorite status for the current user."""

    if request.method == "POST":
        game_id = request.POST.get("game_id")
        game = get_object_or_404(Game, guid=game_id)
        user_preferences = get_object_or_404(UserPreferences, user=request.user)

        # Check if the game is already in the favorites and make the necessary changes
        if game in user_preferences.favorite_games.all():
            user_preferences.favorite_games.remove(game)
            is_favorite = False
        else:
            user_preferences.favorite_games.add(game)
            is_favorite = True

        return JsonResponse({"is_favorite": is_favorite})


@login_required
def toggle_game_queue(request):
    """View for toggling a game's queued status for the current user."""
    if request.method == "POST":
        game_id = request.POST.get("game_id")
        game = get_object_or_404(Game, guid=game_id)
        user_preferences = get_object_or_404(UserPreferences, user=request.user)

        # Check if the game is already in the queue and make the necessary changes
        if game in user_preferences.game_queue.all():
            user_preferences.game_queue.remove(game)
            in_queue = False
        else:
            user_preferences.game_queue.add(game)
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
    user_games = [review.game for review in user_reviews]
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

    # Get the list of games
    games = getattr(user_preferences, f"get_{list_name}")() if not created else []

    current_viewer_preferences, created = UserPreferences.objects.get_or_create(
        user=request.user
    )

    user_friends = get_friend_list(request.user)

    context = {
        "page_title": page_title,
        "user_preferences": user_preferences,
        "games": games,
        "other_user": other_user_profile,
        "user_name": user.userprofile.profile_name,
        "current_viewer_preferences": current_viewer_preferences,
        "user_friends": user_friends,
    }

    return render(request, template_name, context)


def top_rated_games(request):
    """View to display top rated games."""
    user, user_preferences, user_friends = get_user_context(request)

    top_games = Game.objects.filter(average_score__gt=4).order_by("average_score")

    context = {
        "page_title": _("Top Rated Games :: PlayStyle Compass"),
        "games": top_games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
    }

    return render(request, "games/top_rated_games.html", context)


def upcoming_games(request):
    """View the upcoming games."""
    user, user_preferences, user_friends = get_user_context(request)

    current_date = date.today()

    upcoming_filter = Q(release_date__gte=current_date) | Q(
        release_date__regex=r"^\d{4}$", release_date__gte=str(current_date.year)
    )

    upcoming_games = Game.objects.filter(upcoming_filter)
    paginated_games = paginate_matching_games(request, upcoming_games)

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
    game = get_object_or_404(Game, guid=game_id)
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
                "review_deck": escape(form.cleaned_data["review_deck"]),
                "review_description": escape(form.cleaned_data["review_description"]),
                "score": form.cleaned_data["score"],
            }

            Review.objects.create(**review_data)

            followers = Follow.objects.filter(followed=user).select_related("follower")
            for follower in followers:
                follower_user = follower.follower
                profile_url = reverse("users:view_profile", args=[profile_name])
                game_url = reverse("playstyle_compass:view_game", args=[game.guid])

                message = (
                    f'<a class="notification-profile" title="View Profile" href="{profile_url}">{profile_name}</a> '
                    f'has posted a new review for <a class="notification-link" title="View Game" href="{game_url}">{game.title}</a>!'
                )

                create_notification(
                    follower_user,
                    message=message,
                    notification_type="review",
                    profile_url=profile_url,
                    profile_name=profile_name,
                    game_url=game_url,
                    game_title=game.title,
                )

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
    game = get_object_or_404(Game, guid=game_id)
    user = request.user
    next_url = request.GET.get("next", reverse("playstyle_compass:index"))

    try:
        # Attempt to retrieve the user's existing review for the specified game
        review = get_object_or_404(Review, game=game, user=user)
    except (Review.DoesNotExist, Http404):
        # Handle the case where the user hasn't written any reviews for this game
        messages.error(request, _("You haven't written any reviews for this game!"))
        return HttpResponseRedirect(next_url)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            # Escape data before saving
            cleaned_data = form.cleaned_data
            review.review_deck = escape(cleaned_data.get("review_deck", ""))
            review.review_description = escape(
                cleaned_data.get("review_description", "")
            )
            review.score = cleaned_data.get("score")

            review.save()

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
    inactive_user = "inactive-user"

    reviews_data = [
        {
            "id": review.id,
            "reviewer": (
                inactive_user
                if "deactivated-" in str(review.reviewers)
                else review.reviewers
            ),
            "title": review.review_deck,
            "description": review.review_description,
            "score": review.score,
            "likes": review.likes,
            "dislikes": review.dislikes,
            "date_added": localtime(review.date_added).strftime("%d/%m/%Y"),
            "user_id": (
                invalid_user_id if "-" in str(review.user_id) else review.user_id
            ),
        }
        for review in game_reviews
    ]

    return JsonResponse({"reviews": reviews_data})


@login_required
def like_review(request):
    """View used to like / unlike reviews."""
    if request.method == "POST":
        review_id = request.POST.get("review_id")

        if review_id:
            review = get_object_or_404(Review, id=review_id)

            if review.user_id == request.user.id:
                return JsonResponse({"message": _("You cannot like your own review.")})

            if "-" in str(review.user_id):
                review.user_id = -1

            if review.user_has_disliked(request.user.id):
                review.remove_dislike(request.user.id)

            if review.user_has_liked(request.user.id):
                review.remove_like(request.user.id)
            else:
                review.add_like(request.user.id)

            return JsonResponse(
                {"likes": review.likes, "dislikes": review.dislikes, "message": ""}
            )

        return JsonResponse({"error": _("Review ID invalid.")})

    return JsonResponse(
        {"message": _("You must be logged in to like or dislike a review.")}
    )


@login_required
def dislike_review(request):
    """View used to dislike / undislike a review."""
    if request.method == "POST":
        review_id = request.POST.get("review_id")

        if review_id:
            review = get_object_or_404(Review, id=review_id)

            if review.user_id == request.user.id:
                return JsonResponse(
                    {"message": _("You cannot dislike your own review.")}
                )

            if "-" in str(review.user_id):
                review.user_id = -1

            if review.user_has_liked(request.user.id):
                review.remove_like(request.user.id)

            if review.user_has_disliked(request.user.id):
                review.remove_dislike(request.user.id)
            else:
                review.add_dislike(request.user.id)

            return JsonResponse(
                {"dislikes": review.dislikes, "likes": review.likes, "message": ""}
            )

        return JsonResponse({"error": _("Review ID invalid.")})

    return JsonResponse(
        {"message": _("You must be logged in to like or dislike a review.")}
    )


@require_POST
@login_required
def delete_reviews(request, game_id):
    """View for deleting user reviews."""
    game = get_object_or_404(Game, guid=game_id)
    next_url = request.POST.get("next", reverse("playstyle_compass:index"))

    try:
        review = get_object_or_404(Review, game=game, user=request.user)
        review.delete()
        messages.success(request, _("Your review has been successfully deleted!"))
    except (Review.DoesNotExist, Http404):
        messages.error(request, _("You haven't written any reviews for this game!"))

    return HttpResponseRedirect(next_url)


def view_game(request, game_id):
    """View used to display a single game."""
    user, user_preferences, user_friends = get_user_context(request)
    game = get_object_or_404(Game, guid=game_id)

    context = {
        "page_title": f"{game.title} :: PlayStyle Compass",
        "game": game,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "search_bar_type": "search_games",
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
            game = get_object_or_404(Game, guid=game_id)
            receiver = get_object_or_404(User, id=receiver_id)

            # Check if the game is already shared with the receiver
            if SharedGame.objects.filter(
                sender=request.user, receiver=receiver, game_id=game.guid
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
                    <p>Check it out <a href='{reverse('playstyle_compass:view_game', args=[game.guid])}' target='_blank'>here</a>!</p>
                </div>
            """

            # Create a new Message object
            message = SharedGame.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_content,
                game_id=game.guid,
            )

            user_in_notification = request.user.userprofile.profile_name
            profile_url = reverse("users:view_profile", args=[user_in_notification])
            navigation_url = reverse("playstyle_compass:games_shared")

            message = f"""<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a>
                just shared a game with you!<br> 
                <a class="notification-link" title="Navigate" href="{navigation_url}">Navigate to shared games</a>
                """

            create_notification(
                receiver,
                message=message,
                notification_type="shared_game",
                profile_url=profile_url,
                user_in_notification=user_in_notification,
                navigation_url=navigation_url,
            )

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
    sort_order = request.GET.get("sort_order", "asc")
    active_category = request.GET.get("category", "received")

    if active_category == "received":
        games = SharedGame.objects.filter(
            receiver=request.user, is_deleted_by_receiver=False
        )
    elif active_category == "sent":
        games = SharedGame.objects.filter(
            sender=request.user, is_deleted_by_sender=False
        )
    else:
        games = []

    if sort_order == "asc":
        games = games.order_by("timestamp")
    else:
        games = games.order_by("-timestamp")

    context = {
        "page_title": _("Shared Games :: PlayStyle Compass"),
        "games": games,
        "selected_sort_order": sort_order,
        "category": active_category,
    }

    return render(request, "games/games_shared.html", context)


@require_POST
@login_required
def delete_shared_games(request):
    """View used to delete selected shared games."""

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

    category = request.GET.get("category", "")
    sort_order = request.GET.get("sort_order", "")
    games_shared_url = (
        reverse("playstyle_compass:games_shared")
        + f"?category={category}&sort_order={sort_order}"
    )

    return redirect(games_shared_url)


@login_required
def similar_playstyles(request):
    """View used to show users with similar playstyles."""
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)

    preferences_to_compare = [
        "gaming_history",
        "favorite_genres",
        "themes",
        "platforms",
    ]
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


@login_required
def play_histories(request):
    """View used to show users with similar gaming history."""
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)

    # Compare gaming history
    preferences_to_compare = ["gaming_history"]
    similarity_threshold = 0.6

    all_user_prefs = UserPreferences.objects.exclude(user=request.user)

    # Find users with similar gaming history
    similar_user_gaming_history = [
        user
        for user in all_user_prefs
        if calculate_average_similarity(user_preferences, user, preferences_to_compare)
        >= similarity_threshold
    ]

    context = {
        "page_title": _("Kinded Play Histories :: PlayStyle Compass"),
        "similar_user_gaming_history": similar_user_gaming_history,
        "user_preferences": user_preferences,
    }

    return render(request, "misc/play_histories.html", context)


def view_franchises(request):
    """View used to display all franchises."""
    all_franchises = Franchise.objects.all()

    sort_order = request.GET.get("sort_order", "default")
    if sort_order == "asc":
        all_franchises = all_franchises.order_by("title")
    elif sort_order == "desc":
        all_franchises = all_franchises.order_by("-title")
    elif sort_order == "games_asc":
        all_franchises = all_franchises.order_by("games_count")
    elif sort_order == "games_desc":
        all_franchises = all_franchises.order_by("-games_count")

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
        "search_bar_type": "search_franchises",
    }

    return render(request, "franchises/view_franchise.html", context)


def view_characters(request):
    """View used to display all characters."""
    characters = Character.objects.all()

    sort_order = request.GET.get("sort_order", "default")
    if sort_order == "asc":
        characters = characters.order_by("name")
    elif sort_order == "desc":
        characters = characters.order_by("-name")

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
        "search_bar_type": "search_characters",
    }

    return render(request, "characters/game_character.html", context)


def search_characters(request):
    """Retrieves characters from the database that match a given
    search query and renders a search results page.
    """
    query = request.GET.get("query")
    if query and len(query) < 2:
        return HttpResponseBadRequest(
            "Invalid query. Please enter at least 2 characters."
        )

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

    return JsonResponse({"results": results})


def get_games_and_context(request, game_mode):
    """Prepare context data for displaying games based on the specified game mode."""
    user, user_preferences, user_friends = get_user_context(request)

    games_query = GameModes.objects.filter(game_mode=game_mode)
    game_ids = [game.game_id for game in games_query]
    games = Game.objects.filter(guid__in=game_ids)

    additional_games = None
    if game_mode == "Singleplayer":
        additional_games = Game.objects.filter(concepts__icontains="Single-Player Only")
    elif game_mode == "Multiplayer":
        additional_games = Game.objects.filter(
            concepts__icontains="Split-Screen Multiplayer"
        )

    if additional_games is not None:
        games = list(games) + list(additional_games)
        games = Game.objects.filter(pk__in=[game.pk for game in games])

    games = paginate_matching_games(request, games)

    context = {
        "page_title": (
            "Single-player" if game_mode == "Singleplayer" else "Multiplayer"
        )
        + " Games :: PlayStyle Compass",
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return context


def view_multiplayer_games(request):
    """Display multiplayer games."""
    context = get_games_and_context(request, "Multiplayer")

    return render(request, "games/multiplayer_games.html", context)


def view_singleplayer_games(request):
    """Display single-player games."""
    context = get_games_and_context(request, "Singleplayer")

    return render(request, "games/singleplayer_games.html", context)


def game_library(request):
    """View used to display the games library."""
    user, user_preferences, user_friends = get_user_context(request)

    games = Game.objects.all()

    # Gather various game attributes for filtering purposes
    genres, concepts, themes, platforms, franchises = gather_game_attributes(games)

    # Get the selected filters from the request
    selected_filters = get_selected_filters(request)

    # Build a query based on the selected filters
    query = build_query(selected_filters)

    # Apply the filters to the games queryset if any filters are selected
    if any(selected_filters.values()):
        games = games.filter(query)

    sort_by = request.GET.get("sort_by")
    # Sort the games queryset based on the sorting option, if any
    if sort_by:
        games = sort_game_library(games, sort_by)

    # Paginate the filtered and sorted games queryset
    games = paginate_matching_games(request, games)

    context = {
        "page_title": _("Game Library :: PlayStyle Compass"),
        "games": games,
        "genres": sorted(genres),
        "concepts": sorted(concepts),
        "themes": sorted(themes),
        "platforms": sorted(platforms),
        "franchises": sorted(franchises),
        "selected_genres": selected_filters["genres"],
        "selected_concepts": selected_filters["concepts"],
        "selected_themes": selected_filters["themes"],
        "selected_platforms": selected_filters["platforms"],
        "selected_franchises": selected_filters["franchises"],
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
        "query_string": request.GET.urlencode(),
    }

    return render(request, "games/game_library.html", context)


def latest_news(request):
    """View used to display all the gaming news."""
    articles = News.objects.all()

    platforms = get_associated_platforms(articles)
    selected_platform = request.GET.get("platforms")

    if selected_platform:
        articles = articles.filter(platforms__icontains=selected_platform)

    sort_by = request.GET.get("sort_by", "publish_date_desc")

    if sort_by:
        articles = sort_articles(articles, sort_by)

    articles = paginate_objects(request, articles, objects_per_page=21)

    context = {
        "page_title": _("News :: PlayStyle Compass"),
        "articles": articles,
        "platforms": sorted(platforms),
        "selected_platform": selected_platform,
        "query_string": request.GET.urlencode(),
    }

    return render(request, "base/latest_news.html", context)


def similar_games_directory(request):
    """View to display all games with links to their similar games pages, organized alphabetically."""
    games = Game.objects.all().order_by("title")

    # Initialize a dictionary to categorize games by their starting letter
    games_by_letter = {}
    for game in games:
        # Determine the first alphabetical character of the game's title
        first_letter = get_first_letter(game.title)

        # Group games by their starting letter
        if first_letter not in games_by_letter:
            games_by_letter[first_letter] = []
        games_by_letter[first_letter].append(game)

    # Sort the dictionary keys alphabetically and ensure '#' (for non-alphabetical titles) is at the end
    sorted_letters = sorted(games_by_letter.keys() - {"#"})
    if "#" in games_by_letter:
        sorted_letters.append("#")

    # Create a new dictionary with games sorted by letter, including '#' at the end if present
    sorted_games_by_letter = {
        letter: games_by_letter.get(letter, []) for letter in sorted_letters
    }

    context = {
        "page_title": _("Similar Games Directory :: PlayStyle Compass"),
        "games_by_letter": sorted_games_by_letter,
    }

    return render(request, "games/similar_games_directory.html", context)


def similar_games(request, game_guid):
    user, user_preferences, user_friends = get_user_context(request)
    main_game = get_object_or_404(Game, guid=game_guid)
    similar_games = get_similar_games(main_game)
    similar_games = paginate_matching_games(request, similar_games)

    translated_page_title = _("Games like")

    context = {
        "page_title": f"{translated_page_title} {main_game.title} :: PlayStyle Compass",
        "main_game": main_game,
        "similar_games": similar_games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/similar_games.html", context)


def get_filtered_games(request, filter_keyword):
    """Helper function to filter games based on a keyword and paginate the results."""
    user, user_preferences, user_friends = get_user_context(request)

    # Filter games by keyword and order by title
    games = Game.objects.filter(concepts__icontains=filter_keyword).order_by("title")

    # Paginate the filtered games
    games = paginate_matching_games(request, games)

    return games, user_preferences, user_friends


def open_world_games(request):
    """View to display all open world games."""
    games, user_preferences, user_friends = get_filtered_games(request, "Open World")

    context = {
        "page_title": _("Open World Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/open_world_games.html", context)


def linear_gameplay_games(request):
    """View to display all linear gameplay games."""
    games, user_preferences, user_friends = get_filtered_games(
        request, "Linear Gameplay"
    )

    context = {
        "page_title": _("Linear Gameplay Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/linear_gameplay_games.html", context)


def indie_games(request):
    """View to display all Indie games."""
    games, user_preferences, user_friends = get_filtered_games(request, "Indie")

    context = {
        "page_title": _("Indie Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/indie_games.html", context)


def steam_games(request):
    """View to display all Steam games."""
    games, user_preferences, user_friends = get_filtered_games(request, "Steam")

    context = {
        "page_title": _("Steam Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/steam_games.html", context)


def free_to_play_games(request):
    """View to display all Free to Play games."""
    games, user_preferences, user_friends = get_filtered_games(request, "Free to Play")

    context = {
        "page_title": _("Free to Play Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/free_to_play_games.html", context)


def vr_games(request):
    """View to display all Virtual Reality games."""
    games, user_preferences, user_friends = get_filtered_games(
        request, "Virtual Reality"
    )

    context = {
        "page_title": _("VR Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/vr_games.html", context)


def beginner_games(request):
    """View to display all Beginner-Friendly games."""
    user, user_preferences, user_friends = get_user_context(request)
    games = Game.objects.filter(is_casual=True)
    games = paginate_matching_games(request, games)

    context = {
        "page_title": _("Beginner Games :: PlayStyle Compass"),
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/beginner_games.html", context)


@login_required
def create_game_list(request):
    """View used to create a game list."""
    if request.method == "POST":
        form = GameListForm(request.POST)
        if form.is_valid():
            game_list = form.save(commit=False)
            game_list.owner = request.user
            game_list.save()

            return redirect("playstyle_compass:game_list_detail", pk=game_list.pk)
    else:
        form = GameListForm()

    context = {
        "page_title": _("Create Game List :: PlayStyle Compass"),
        "form": form,
    }

    return render(request, "game_list/create_game_list.html", context)


@login_required
def edit_game_list(request, pk):
    """View to edit an existing game list."""
    game_list = get_object_or_404(GameList, pk=pk)

    if game_list.owner != request.user:
        return redirect("playstyle_compass:game_list_detail", pk=game_list.pk)

    if request.method == "POST":
        form = GameListForm(request.POST, instance=game_list)
        if form.is_valid():
            form.save()
            return redirect("playstyle_compass:game_list_detail", pk=game_list.pk)
    else:
        form = GameListForm(instance=game_list)

    context = {
        "page_title": _("Edit Game List :: PlayStyle Compass"),
        "form": form,
        "game_list": game_list,
    }

    return render(request, "game_list/edit_game_list.html", context)


@login_required
def delete_game_list(request, pk):
    """View used to delete a game list."""
    game_list = get_object_or_404(GameList, pk=pk)

    if game_list.owner == request.user:
        game_list.delete()
        messages.success(request, "Game list deleted successfully.")
    else:
        messages.error(request, "You are not allowed to delete this game list.")
        return redirect("playstyle_compass:game_list_detail", pk=game_list.pk)

    return redirect("playstyle_compass:user_game_lists", user_id=request.user.id)


@login_required
def delete_all_game_lists(request):
    """View used to delete all game lists for the logged-in user."""
    if request.method == "POST":
        game_lists = GameList.objects.filter(owner=request.user)

        deleted_count, _ = game_lists.delete()

        if deleted_count > 0:
            messages.success(
                request, f"{deleted_count} game lists deleted successfully."
            )
        else:
            messages.error(request, "You have no game lists to delete.")

    return redirect("playstyle_compass:user_game_lists", user_id=request.user.id)


def game_list_detail(request, pk):
    """View used to view a game list."""
    game_list = get_object_or_404(GameList, pk=pk)
    games = paginate_matching_games(
        request, Game.objects.filter(guid__in=game_list.game_guids)
    )
    additional_games = (
        game_list.additional_games.split(",") if game_list.additional_games else []
    )
    user, user_preferences, user_friends = get_user_context(request)

    reviews = ListReview.objects.filter(game_list=game_list).order_by("-created_at")
    review_form = ListReviewForm()
    review = ListReview.objects.filter(game_list=game_list, user=user).first()

    comment_form = ListCommentForm()
    comments = ListComment.objects.filter(game_list=game_list).order_by("created_at")

    context = {
        "page_title": _("View Game List :: PlayStyle Compass"),
        "game_list": game_list,
        "games": games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
        "additional_games": additional_games,
        "reviews": reviews,
        "form": review_form,
        "review": review,
        "comment_form": comment_form,
        "comments": comments,
    }

    return render(request, "game_list/game_list_detail.html", context)


@login_required
def share_game_list(request, pk):
    """View used to share a game list."""
    game_list = GameList.objects.get(pk=pk)

    if request.method == "POST":
        users_to_share_with = request.POST.getlist("shared_with")

        if not users_to_share_with:
            return HttpResponseBadRequest(
                "At least one friend must be selected to share the game list."
            )

        game_list.shared_with.add(*users_to_share_with)

        # Initialize or update 'shared_by' to track who shared the list
        shared_by_info = game_list.shared_by or {}

        sharer_id = str(request.user.id)
        if sharer_id not in shared_by_info:
            shared_by_info[sharer_id] = []

        for user_id in users_to_share_with:
            receiver = User.objects.get(pk=user_id)

            if user_id not in shared_by_info[sharer_id]:
                shared_by_info[sharer_id].append(user_id)

            # Create a notification for the user receiving the shared list
            profile_url = reverse(
                "users:view_profile", args=[request.user.userprofile.profile_name]
            )
            game_list_url = reverse(
                "playstyle_compass:game_list_detail", args=[game_list.pk]
            )
            message = format_html(
                '<a class="notification-profile" href="{}">{}</a> has shared a game list with you <a href="{}">{}</a>',
                profile_url,
                request.user.userprofile.profile_name,
                game_list_url,
                game_list.title,
            )
            create_notification(
                receiver,
                message=message,
                notification_type="shared_game_list",
                profile_url=profile_url,
                profile_name=request.user.userprofile.profile_name,
                game_list_url=game_list_url,
                game_list_title=game_list.title,
            )

        game_list.shared_by = shared_by_info
        game_list.save()

        messages.success(request, _("Game list successfully shared!"))
        return redirect("playstyle_compass:game_list_detail", pk=game_list.pk)

    user, user_preferences, user_friends = get_user_context(request)

    context = {
        "page_title": _("Share Game List :: PlayStyle Compass"),
        "game_list": game_list,
        "user_friends": user_friends,
    }

    return render(request, "game_list/share_game_list.html", context)


def user_game_lists(request, user_id):
    """View used to display game lists of a user with sorting options."""
    user = get_object_or_404(User, id=user_id)
    game_lists = GameList.objects.filter(owner=user)

    sort_by = request.GET.get("sort_by", "created_at")
    order = request.GET.get("order", "desc")
    reverse_order = order == "desc"

    game_lists = list(game_lists)

    if sort_by == "title":
        game_lists.sort(key=lambda x: x.title.lower(), reverse=reverse_order)
    elif sort_by == "total_games":
        game_lists.sort(key=lambda x: x.total_games, reverse=reverse_order)
    elif sort_by == "created_at":
        game_lists.sort(key=lambda x: x.created_at, reverse=reverse_order)
    elif sort_by == "share_count":
        game_lists.sort(key=lambda x: x.share_count, reverse=reverse_order)
    elif sort_by == "like_count":
        game_lists.sort(key=lambda x: x.like_count, reverse=reverse_order)
    elif sort_by == "review_count":
        game_lists.sort(key=lambda x: x.review_count, reverse=reverse_order)
    elif sort_by == "updated_at":
        game_lists.sort(key=lambda x: x.updated_at, reverse=reverse_order)
    elif sort_by == "activity_level":
        game_lists.sort(
            key=lambda x: (x.share_count + x.like_count + x.review_count),
            reverse=reverse_order,
        )

    context = {
        "page_title": _("Game Lists :: PlayStyle Compass"),
        "game_lists": game_lists,
        "list_user": user,
        "sort_by": sort_by,
        "order": order,
    }

    return render(request, "game_list/user_game_lists.html", context)


@login_required
def shared_game_lists(request):
    """View to display game lists shared with and by the user."""
    user = request.user
    view_type = request.GET.get("view", "received")
    sort_by = request.GET.get("sort_by", "title")
    order = request.GET.get("order", "desc")

    if view_type == "shared":
        game_lists = GameList.objects.all()
        game_lists = [
            game_list
            for game_list in game_lists
            if str(user.id) in game_list.shared_by and game_list.shared_by[str(user.id)]
        ]
        page_title = _("Game Lists You Shared with Others")
    else:
        # Get lists that have been shared with the user
        game_lists = GameList.objects.filter(shared_with=user)
        page_title = _("Game Lists Shared With You")

        # Track all users who shared the list with the current user
        for game_list in game_lists:
            shared_by_user_ids = [
                sharer_id
                for sharer_id, receivers in game_list.shared_by.items()
                if str(user.id) in receivers
            ]

            # Attach users who shared the game list
            game_list.shared_by_users = (
                User.objects.filter(id__in=shared_by_user_ids)
                if shared_by_user_ids
                else []
            )

    game_lists = list(game_lists)

    if sort_by == "title":
        game_lists.sort(key=lambda x: x.title.lower(), reverse=(order == "desc"))
    elif sort_by == "total_games":
        game_lists.sort(key=lambda x: x.total_games, reverse=(order == "desc"))

    context = {
        "page_title": page_title,
        "game_lists": game_lists,
        "view_type": view_type,
        "sort_by": sort_by,
        "order": order,
    }

    return render(request, "game_list/shared_game_lists.html", context)


@login_required
def like_game_list(request, list_id):
    """Toggles the like status for a game list."""
    game_list = get_object_or_404(GameList, id=list_id)

    if request.user in game_list.liked_by.all():
        game_list.liked_by.remove(request.user)
        liked = False
    else:
        game_list.liked_by.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "like_count": game_list.like_count})


@login_required
@require_POST
def review_game_list(request, game_list_id):
    """Create or update a review for a specific game list."""
    game_list = get_object_or_404(GameList, id=game_list_id)
    existing_review = ListReview.objects.filter(
        game_list=game_list, user=request.user
    ).first()

    if existing_review:
        form = ListReviewForm(request.POST, instance=existing_review)
    else:
        form = ListReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.game_list = game_list
        review.save()

        return JsonResponse(
            {
                "message": _("Review submitted successfully!"),
                "review_id": review.id,
                "title": review.title,
                "rating": review.rating,
                "created_at": review.created_at,
                "review_text": review.review_text,
                "author": review.user.userprofile.profile_name,
            }
        )

    return JsonResponse({"errors": form.errors}, status=400)


@login_required
@require_POST
def edit_game_list_review(request, review_id):
    """Edit an existing review."""
    review = get_object_or_404(ListReview, id=review_id, user=request.user)

    form = ListReviewForm(request.POST, instance=review)

    if form.is_valid():
        form.save()
        return JsonResponse(
            {
                "message": _("Review updated successfully!"),
                "review_id": review.id,
                "title": review.title,
                "author": review.user.userprofile.profile_name,
                "rating": review.rating,
                "created_at": review.created_at,
                "review_text": review.review_text,
            }
        )

    return JsonResponse({"errors": form.errors}, status=400)


@login_required
@require_POST
def delete_game_list_review(request, review_id):
    """Delete a specific review for a game list."""
    review = get_object_or_404(ListReview, id=review_id, user=request.user)
    review.delete()

    return JsonResponse({"message": _("Review deleted successfully!")})


@login_required
def like_game_list_review(request, review_id):
    """Toggles the like status for a review."""
    review = get_object_or_404(ListReview, id=review_id)

    if request.user in review.liked_by.all():
        review.liked_by.remove(request.user)
        liked = False
    else:
        review.liked_by.add(request.user)
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "like_count": review.like_count,
            "review_id": review_id,
        }
    )


@login_required
def reviewed_game_lists(request, user_id=None):
    """View to get the reviewed game lists."""
    # Determine the user based on the provided user_id or the authenticated user
    user = request.user if user_id is None else get_object_or_404(User, id=user_id)

    other_user_profile = user != request.user
    user_preferences, created = UserPreferences.objects.get_or_create(user=user)

    # Retrieve reviewed game lists
    reviewed_lists = ListReview.objects.filter(user=user)
    reviewed_game_lists = [review.game_list for review in reviewed_lists]

    current_viewer_preferences, created = UserPreferences.objects.get_or_create(
        user=request.user
    )

    user_friends = get_friend_list(request.user)

    context = {
        "page_title": _("Reviewed Game Lists :: PlayStyle Compass"),
        "game_lists": reviewed_game_lists,
        "user_preferences": user_preferences,
        "other_user": other_user_profile,
        "list_user": user,
        "current_viewer_preferences": current_viewer_preferences,
        "user_friends": user_friends,
    }

    return render(request, "game_list/reviewed_game_lists.html", context)


@login_required
def privacy_settings(request):
    user_preferences = get_object_or_404(UserPreferences, user=request.user)

    if request.method == "POST":
        form = PrivacySettingsForm(request.POST, instance=user_preferences)
        if form.is_valid():
            form.save()
            return redirect("playstyle_compass:privacy_settings")
    else:
        form = PrivacySettingsForm(instance=user_preferences)

    context = {
        "page_title": _("Privacy Settings :: PlayStyle Compass"),
        "form": form,
    }

    return render(request, "preferences/privacy_settings.html", context)


def explore_game_lists(request):
    """View used to explore public game lists."""
    game_lists = GameList.objects.filter(is_public=True)

    sort_by = request.GET.get("sort_by", "created_at")
    order = request.GET.get("order", "desc")
    reverse_order = order == "desc"

    game_lists = list(game_lists)

    if sort_by == "title":
        game_lists.sort(key=lambda x: x.title.lower(), reverse=reverse_order)
    elif sort_by == "total_games":
        game_lists.sort(key=lambda x: x.total_games, reverse=reverse_order)
    elif sort_by == "created_at":
        game_lists.sort(key=lambda x: x.created_at, reverse=reverse_order)
    elif sort_by == "share_count":
        game_lists.sort(key=lambda x: x.share_count, reverse=reverse_order)
    elif sort_by == "like_count":
        game_lists.sort(key=lambda x: x.like_count, reverse=reverse_order)
    elif sort_by == "review_count":
        game_lists.sort(key=lambda x: x.review_count, reverse=reverse_order)
    elif sort_by == "updated_at":
        game_lists.sort(key=lambda x: x.updated_at, reverse=reverse_order)
    elif sort_by == "activity_level":
        game_lists.sort(
            key=lambda x: (x.share_count + x.like_count + x.review_count),
            reverse=reverse_order,
        )

    context = {
        "page_title": _("Explore Game Lists :: PlayStyle Compass"),
        "game_lists": game_lists,
        "sort_by": sort_by,
        "order": order,
    }

    return render(request, "game_list/explore_game_lists.html", context)


@login_required
def delete_list_comment(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(ListComment, id=comment_id, user=request.user)
        comment.delete()
        return JsonResponse({"success": True}, status=200)

    return JsonResponse({"success": False}, status=400)


@login_required
def edit_list_comment(request, comment_id):
    comment = get_object_or_404(ListComment, id=comment_id, user=request.user)

    if not comment.is_editable():
        return JsonResponse(
            {"error": _("You can no longer edit this comment.")}, status=403
        )

    if request.method == "POST":
        form = ListCommentForm(request.POST, instance=comment)

        if form.is_valid():
            if not form.cleaned_data["text"].strip():
                return JsonResponse(
                    {"success": False, "error": _("Comment text cannot be empty.")},
                    status=400,
                )

            updated_comment = form.save()

            profile_url = reverse(
                "users:view_profile",
                kwargs={"profile_name": request.user.userprofile.profile_name},
            )

            created_at = localtime(comment.created_at).strftime("%d/%m/%Y - %H:%M")

            response_data = {
                "success": True,
                "message": _("Comment updated successfully."),
                "comment_text": updated_comment.text,
                "created_at": created_at,
                "profile_url": profile_url,
                "profile_name": request.user.userprofile.profile_name,
                "delete_url": reverse(
                    "playstyle_compass:delete_list_comment", args=[updated_comment.id]
                ),
                "edit_url": reverse(
                    "playstyle_compass:edit_list_comment", args=[updated_comment.id]
                ),
            }

            return JsonResponse(response_data)
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = ListCommentForm(instance=comment)
        form_html = render_to_string(
            "game_list/edit_comment_form.html", {"form": form}, request=request
        )
        return JsonResponse({"form": form_html})


@login_required
def post_list_comment(request, game_list_id):
    game_list = get_object_or_404(GameList, id=game_list_id)

    if request.method == "POST":
        comment_text = request.POST.get("text")
        if comment_text:
            comment = ListComment.objects.create(
                user=request.user, text=comment_text, game_list=game_list
            )

            profile_url = reverse(
                "users:view_profile",
                kwargs={"profile_name": request.user.userprofile.profile_name},
            )
            created_at = localtime(comment.created_at).strftime("%d/%m/%Y - %H:%M")

            # Return the response with the necessary data
            return JsonResponse(
                {
                    "success": True,
                    "comment_text": comment.text,
                    "profile_url": profile_url,
                    "profile_name": request.user.userprofile.profile_name,
                    "created_at": created_at,
                    "delete_url": reverse(
                        "playstyle_compass:delete_list_comment", args=[comment.id]
                    ),
                    "edit_url": reverse(
                        "playstyle_compass:edit_list_comment", args=[comment.id]
                    ),
                }
            )
        else:
            return JsonResponse({"success": False, "error": "Comment text is required"})

    return JsonResponse({"success": False, "error": "Invalid method"})


@login_required
def like_game_list_comment(request, comment_id):
    """Toggles the like status for a comment."""
    comment = get_object_or_404(ListComment, id=comment_id)

    if request.user in comment.liked_by.all():
        comment.liked_by.remove(request.user)
        liked = False
    else:
        comment.liked_by.add(request.user)
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "like_count": comment.like_count,
            "comment_id": comment_id,
        }
    )


@login_required
def toggle_favorite_game_list(request, game_list_id):
    game_list = get_object_or_404(GameList, id=game_list_id)
    is_favorited = game_list.toggle_favorite(request.user)

    return JsonResponse({"favorited": is_favorited})


@login_required
def favorite_game_lists(request, user_id=None):
    """View to display favorite game lists for the specified user."""
    if user_id:
        user = get_object_or_404(User, id=user_id)
        other_user = user != request.user
    else:
        user = request.user
        other_user = False

    game_lists = GameList.objects.filter(favorites=user)

    sort_by = request.GET.get("sort_by", "created_at")
    order = request.GET.get("order", "desc")
    reverse_order = order == "desc"

    game_lists = list(game_lists)

    if sort_by == "title":
        game_lists.sort(key=lambda x: x.title.lower(), reverse=reverse_order)
    elif sort_by == "total_games":
        game_lists.sort(key=lambda x: x.total_games, reverse=reverse_order)
    elif sort_by == "created_at":
        game_lists.sort(key=lambda x: x.created_at, reverse=reverse_order)
    elif sort_by == "share_count":
        game_lists.sort(key=lambda x: x.share_count, reverse=reverse_order)
    elif sort_by == "like_count":
        game_lists.sort(key=lambda x: x.like_count, reverse=reverse_order)
    elif sort_by == "review_count":
        game_lists.sort(key=lambda x: x.review_count, reverse=reverse_order)
    elif sort_by == "updated_at":
        game_lists.sort(key=lambda x: x.updated_at, reverse=reverse_order)
    elif sort_by == "activity_level":
        game_lists.sort(
            key=lambda x: (x.share_count + x.like_count + x.review_count),
            reverse=reverse_order,
        )

    context = {
        "page_title": _("Favorite Game Lists :: PlayStyle Compass"),
        "game_lists": game_lists,
        "sort_by": sort_by,
        "order": order,
        "other_user": other_user,
        "viewing_user": user.userprofile.profile_name,
    }

    return render(request, "game_list/favorite_game_lists.html", context)


def popular_games(request):
    """View to display popular games."""
    user, user_preferences, user_friends = get_user_context(request)

    popular_games = Game.objects.filter(is_popular=True)
    popular_games = paginate_matching_games(request, popular_games)

    context = {
        "page_title": _("Popular Games :: PlayStyle Compass"),
        "games": popular_games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
    }

    return render(request, "games/popular_games.html", context)


@login_required
def create_poll(request):
    """View used to create a poll."""
    if request.method == "POST":
        options = request.POST.getlist("options")
        combined_options = "\n".join(opt.strip() for opt in options if opt.strip())

        post_data = request.POST.copy()
        post_data["options"] = combined_options

        form = PollForm(post_data)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user
            poll.save()

            for option_text in options:
                if option_text.strip():
                    PollOption.objects.create(poll=poll, text=option_text.strip())

            messages.success(request, _("Poll successfully created!"))
            return redirect("playstyle_compass:poll_detail", poll_id=poll.pk)
        else:
            return render(request, "polls/create_poll.html", {"form": form})

    else:
        form = PollForm()

    context = {"page_title": _("Create Poll :: PlayStyle Compass"), "form": form}
    return render(request, "polls/create_poll.html", context)


@login_required
def vote(request, id):
    """View used to vote on a poll."""
    poll = get_object_or_404(Poll, id=id)

    if poll.has_ended():
        messages.warning(request, "This poll has ended. Voting is no longer available.")
        redirect_url = request.META.get(
            "HTTP_REFERER", reverse("playstyle_compass:community_polls")
        )
        return redirect(redirect_url)

    if Vote.objects.filter(poll=poll, user=request.user).exists():
        messages.warning(request, "You have already voted in this poll!")
        redirect_url = request.META.get(
            "HTTP_REFERER", reverse("playstyle_compass:community_polls")
        )
        return redirect(redirect_url)

    if request.method == "POST":
        form = VoteForm(poll=poll, data=request.POST)
        if form.is_valid():
            Vote.objects.create(
                poll=poll, option=form.cleaned_data["option"], user=request.user
            )
            messages.success(request, "Your vote has been recorded.")
            redirect_url = request.META.get(
                "HTTP_REFERER", reverse("playstyle_compass:community_polls")
            )
            return redirect(redirect_url)
        else:
            messages.error(request, "There was an error with your vote.")
            redirect_url = request.META.get(
                "HTTP_REFERER", reverse("playstyle_compass:community_polls")
            )
            return redirect(redirect_url)

    return HttpResponseRedirect(reverse("playstyle_compass:community_polls"))


def community_polls(request):
    """View used to display polls."""
    polls = Poll.objects.filter(is_public=True).order_by("-created_at")
    polls = paginate_objects(request, polls)
    user_votes = {}

    polls_with_data = []
    for poll in polls:
        poll.vote_form = VoteForm(poll=poll)

        user_vote = poll.user_vote(request.user)
        if user_vote:
            user_votes[poll.id] = user_vote.id

        options_with_percentages = poll.options_with_percentages()

        polls_with_data.append(
            {
                "poll": poll,
                "total_votes": poll.total_votes(),
                "options_with_percentages": options_with_percentages,
            }
        )

    context = {
        "page_title": _("Community Polls :: PlayStyle Compass"),
        "polls_with_data": polls_with_data,
        "polls": polls,
        "user_votes": user_votes,
        "pagination": True,
    }
    return render(request, "polls/community_polls.html", context)


@login_required
def user_polls(request, user_id):
    """View to display polls created by a specific user."""
    user = get_object_or_404(User, id=user_id)
    polls = Poll.objects.filter(created_by=user).order_by("-created_at")

    user_votes = {}
    polls_with_data = []
    for poll in polls:
        user_vote = poll.user_vote(request.user)
        if user_vote:
            user_votes[poll.id] = user_vote.id

        options_with_percentages = poll.options_with_percentages()

        polls_with_data.append(
            {
                "poll": poll,
                "total_votes": poll.total_votes(),
                "options_with_percentages": options_with_percentages,
            }
        )

    context = {
        "page_title": _("User Polls :: PlayStyle Compass"),
        "polls_with_data": polls_with_data,
        "user_votes": user_votes,
        "user_polls": user,
        "is_own_polls": request.user == user,
    }
    return render(request, "polls/user_polls.html", context)


@login_required
def delete_poll(request, poll_id):
    """View to delete a specific poll."""
    poll = get_object_or_404(Poll, id=poll_id)

    if poll.created_by != request.user:
        messages.error(request, "You are not authorized to delete this poll.")
        return redirect("playstyle_compass:user_polls", user_id=request.user.id)

    poll.delete()
    messages.success(request, "Poll deleted successfully.")
    return redirect("playstyle_compass:user_polls", user_id=request.user.id)


@login_required
def voted_polls(request):
    """View to display polls that the user has voted on."""
    votes = Vote.objects.filter(user=request.user)
    voted_polls = Poll.objects.filter(id__in=[vote.poll.id for vote in votes]).order_by(
        "-created_at"
    )

    user_votes = {}
    polls_with_data = []
    for poll in voted_polls:
        user_vote = poll.user_vote(request.user)
        if user_vote:
            user_votes[poll.id] = user_vote.id

        options_with_percentages = poll.options_with_percentages()

        polls_with_data.append(
            {
                "poll": poll,
                "total_votes": poll.total_votes(),
                "options_with_percentages": options_with_percentages,
            }
        )

    context = {
        "page_title": _("Voted Polls:: PlayStyle Compass"),
        "polls_with_data": polls_with_data,
        "user_votes": user_votes,
    }
    return render(request, "polls/voted_polls.html", context)


@login_required
def like_poll(request, poll_id):
    """Toggles the like status for a poll."""
    poll = get_object_or_404(Poll, id=poll_id)

    if request.user in poll.liked_by.all():
        poll.liked_by.remove(request.user)
        liked = False
    else:
        poll.liked_by.add(request.user)
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "like_count": poll.like_count,
            "poll_id": poll_id,
        }
    )


@login_required
def poll_detail(request, poll_id):
    """View to display the details of a specific poll."""
    poll = get_object_or_404(Poll, id=poll_id)

    # Get user vote for the current poll (if any)
    user_vote = poll.user_vote(request.user)
    user_votes = {poll.id: user_vote.id} if user_vote else {}

    # Prepare options with percentages
    options_with_percentages = poll.options_with_percentages()

    context = {
        "page_title": _("Poll Detail :: PlayStyle Compass"),
        "poll": poll,
        "total_votes": poll.total_votes(),
        "options_with_percentages": options_with_percentages,
        "user_votes": user_votes,
    }
    return render(request, "polls/poll_detail.html", context)


@login_required
def share_poll(request, poll_id):
    """View used to share a poll."""
    poll = Poll.objects.get(id=poll_id)

    if request.method == "POST":
        users_to_share_with = request.POST.getlist("shared_with")

        if not users_to_share_with:
            return HttpResponseBadRequest(
                "At least one friend must be selected to share the poll."
            )

        poll.shared_with.add(*users_to_share_with)

        # Initialize or update 'shared_by' to track who shared the poll
        shared_by_info = poll.shared_by or {}

        sharer_id = str(request.user.id)
        if sharer_id not in shared_by_info:
            shared_by_info[sharer_id] = []

        for user_id in users_to_share_with:
            receiver = User.objects.get(pk=user_id)

            if user_id not in shared_by_info[sharer_id]:
                shared_by_info[sharer_id].append(user_id)

            # Create a notification for the user receiving the shared poll
            profile_url = reverse(
                "users:view_profile", args=[request.user.userprofile.profile_name]
            )
            poll_url = reverse("playstyle_compass:poll_detail", args=[poll.pk])
            message = format_html(
                '<a class="notification-profile" href="{}">{}</a> has shared a poll with you <a href="{}">{}</a>',
                profile_url,
                request.user.userprofile.profile_name,
                poll_url,
                poll.title,
            )
            create_notification(
                receiver,
                message=message,
                notification_type="shared_poll",
                profile_url=profile_url,
                profile_name=request.user.userprofile.profile_name,
                poll_url=poll_url,
                poll_title=poll.title,
            )

        poll.shared_by = shared_by_info
        poll.save()

        messages.success(request, _("Poll successfully shared!"))
        return redirect("playstyle_compass:poll_detail", poll_id=poll.pk)

    user, user_preferences, user_friends = get_user_context(request)

    context = {
        "page_title": _("Share Poll :: PlayStyle Compass"),
        "poll": poll,
        "user_friends": user_friends,
    }

    return render(request, "polls/share_poll.html", context)


@login_required
def shared_polls(request):
    """View to display polls shared with and by the user."""
    user = request.user
    view_type = request.GET.get("view", "received")
    sort_by = request.GET.get("sort_by", "title")
    order = request.GET.get("order", "desc")

    if view_type == "shared":
        polls = Poll.objects.all()
        polls = [
            poll
            for poll in polls
            if str(user.id) in poll.shared_by and poll.shared_by[str(user.id)]
        ]
        page_title = _("Polls You Shared with Others")
    else:
        # Get polls that have been shared with the user
        polls = Poll.objects.filter(shared_with=user)
        page_title = _("Polls Shared With You")

        # Track all users who shared the poll with the current user
        for poll in polls:
            shared_by_user_ids = [
                sharer_id
                for sharer_id, receivers in poll.shared_by.items()
                if str(user.id) in receivers
            ]

            # Attach users who shared the poll
            poll.shared_by_users = (
                User.objects.filter(id__in=shared_by_user_ids)
                if shared_by_user_ids
                else []
            )

    polls = list(polls)

    if sort_by == "title":
        polls.sort(key=lambda x: x.title.lower(), reverse=(order == "desc"))
    elif sort_by == "created_at":
        polls.sort(key=lambda x: x.created_at, reverse=(order == "desc"))

    context = {
        "page_title": page_title,
        "polls": polls,
        "view_type": view_type,
        "sort_by": sort_by,
        "order": order,
    }

    return render(request, "polls/shared_polls.html", context)


@login_required
def completed_polls(request):
    """View to display all completed polls."""
    all_polls = Poll.objects.all().order_by("-created_at")
    all_polls = paginate_objects(request, all_polls)

    completed_polls = [poll for poll in all_polls if poll.has_ended()]

    user_votes = {}
    polls_with_data = []
    for poll in completed_polls:
        user_vote = poll.user_vote(request.user)
        if user_vote:
            user_votes[poll.id] = user_vote.id

        options_with_percentages = poll.options_with_percentages()

        polls_with_data.append(
            {
                "poll": poll,
                "total_votes": poll.total_votes(),
                "options_with_percentages": options_with_percentages,
            }
        )

    context = {
        "page_title": _("Completed Polls :: PlayStyle Compass"),
        "polls_with_data": polls_with_data,
        "polls": all_polls,
        "user_votes": user_votes,
        "pagination": True,
    }
    return render(request, "polls/completed_polls.html", context)


def deals_list(request):
    sort_order = request.GET.get("sort_order", "game_name_asc")
    store_name = request.GET.get("store_name", "")

    all_deals = Deal.objects.all()

    if store_name:
        all_deals = all_deals.filter(store_name=store_name)

    if sort_order == "sale_desc":
        all_deals = all_deals.order_by("-sale_price")
    elif sort_order == "sale_asc":
        all_deals = all_deals.order_by("sale_price")
    elif sort_order == "game_name_desc":
        all_deals = all_deals.order_by("-game_name")
    elif sort_order == "game_name_asc":
        all_deals = all_deals.order_by("game_name")

    deals = paginate_objects(request, all_deals, objects_per_page=28)

    # Get distinct store names for filter dropdown
    available_stores = Deal.objects.values_list("store_name", flat=True).distinct()

    context = {
        "page_title": _("Game Deals :: PlayStyle Compass"),
        "deals": deals,
        "sort_order": sort_order,
        "current_store_name": store_name,
        "available_stores": available_stores,
        "pagination": True,
    }

    return render(request, "deals/deals.html", context)


@login_required
def game_reviews(request):
    """View used to display game reviews."""
    user = request.user
    sort_order = request.GET.get("sort_order", "date_desc")

    all_reviews = Review.objects.all()

    if sort_order == "date_desc":
        all_reviews = all_reviews.order_by("-date_added")
    elif sort_order == "date_asc":
        all_reviews = all_reviews.order_by("date_added")
    elif sort_order == "score_desc":
        all_reviews = all_reviews.order_by("-score")
    elif sort_order == "score_asc":
        all_reviews = all_reviews.order_by("score")
    elif sort_order == "likes_desc":
        all_reviews = all_reviews.order_by("-likes")
    elif sort_order == "likes_asc":
        all_reviews = all_reviews.order_by("likes")

    reviews = paginate_objects(request, all_reviews)

    context = {
        "page_title": _("Game Reviews :: PlayStyle Compass"),
        "reviews": reviews,
        "pagination": True,
        "sort_order": sort_order,
    }

    return render(request, "reviews/game_reviews.html", context)


def game_deal(request, deal_id):
    deal = Deal.objects.get(deal_id=deal_id)

    context = {
        "page_title": _("Deal Details :: PlayStyle Compass"),
        "deal": deal,
    }

    return render(request, "deals/game_deal.html", context)


@login_required
def share_deal(request, deal_id):
    deal = get_object_or_404(Deal, pk=deal_id)
    user_friends = get_friend_list(request.user)

    if request.method == "POST":
        selected_ids = request.POST.getlist("shared_with")
        for friend_id in selected_ids:
            recipient = get_object_or_404(User, pk=friend_id)
            if recipient != request.user:
                SharedDeal.objects.get_or_create(
                    sender=request.user, recipient=recipient, deal=deal
                )
        messages.success(request, _("Deal shared successfully."))

    context = {
        "page_title": _("Share Deal :: PlayStyle Compass"),
        "deal_id": deal_id,
        "user_friends": user_friends,
    }

    return render(request, "deals/share_deal.html", context)


@login_required
def shared_deals_view(request):
    view_type = request.GET.get("view", "received")
    if view_type == "shared":
        deals = SharedDeal.objects.filter(sender=request.user).select_related(
            "deal", "recipient"
        )
    else:
        deals = SharedDeal.objects.filter(recipient=request.user).select_related(
            "deal", "sender"
        )

    context = {
        "page_title": _("Shared Deals :: PlayStyle Compass"),
        "view_type": view_type,
        "deals": deals,
    }

    return render(request, "deals/shared_deals.html", context)
