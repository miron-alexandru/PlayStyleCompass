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
    path(
        "save_all_preferences/", views.save_all_preferences, name="save_all_preferences"
    ),
]
