"""Defines URL patterns."""

from django.urls import path

from . import views

app_name = "playstyle_compass"

urlpatterns = [
    path("", views.index, name="index"),
    path("gaming_preferences/", views.gaming_preferences, name="gaming_preferences"),
    path("preferences/", views.update_preferences, name="update_preferences"),
    path("get-recommendations/", views.get_recommendations, name="get_recommendations"),
    path("search/", views.search_results, name="search_results"),
    path("autocomplete/", views.autocomplete_view, name="autocomplete"),
    path("clear_preferences/", views.clear_preferences, name="clear_preferences"),
    path("save_gaming_history/", views.save_gaming_history, name="save_gaming_history"),
    path(
        "save_favorite_genres/", views.save_favorite_genres, name="save_favorite_genres"
    ),
    path("save_platforms/", views.save_platforms, name="save_platforms"),
    path("toggle_favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorite_games/", views.favorite_games, name="favorite_games"),
    path("top_rated_games/", views.top_rated_games, name="top_rated_games"),
    path("game/<int:game_id>/add_review/", views.add_review, name="add_review"),
    path("clear_reviews/<int:game_id>/", views.delete_reviews, name="delete_reviews"),
    path(
        "get_game_reviews/<int:game_id>/",
        views.get_game_reviews,
        name="get_game_reviews",
    ),
    path(
        "get_average_score/<int:game_id>/",
        views.get_average_score,
        name="get_average_score",
    ),
    path(
        "edit_review/<int:game_id>/",
        views.edit_review,
        name="edit_review",
    ),
]
