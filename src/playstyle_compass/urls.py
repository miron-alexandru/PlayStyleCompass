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
    path("autocomplete/games/", views.autocomplete_games, name="autocomplete"),
    path("clear_preferences/", views.clear_preferences, name="clear_preferences"),
    path("save_gaming_history/", views.save_gaming_history, name="save_gaming_history"),
    path(
        "save_favorite_genres/", views.save_favorite_genres, name="save_favorite_genres"
    ),
    path("save_themes/", views.save_themes, name="save_themes"),
    path("save_platforms/", views.save_platforms, name="save_platforms"),
    path(
        "save_all_preferences/", views.save_all_preferences, name="save_all_preferences"
    ),
    path(
        "save_connection_types/",
        views.save_connection_types,
        name="save_connection_types",
    ),
    path("save_game_styles/", views.save_game_styles, name="save_game_styles"),
    path("toggle_favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorite_games/", views.favorite_games, name="favorite_games"),
    path(
        "favorite_games/<int:user_id>/",
        views.favorite_games,
        name="favorite_games_with_id",
    ),
    path("top_rated_games/", views.top_rated_games, name="top_rated_games"),
    path("game/<int:game_id>/add_review/", views.add_review, name="add_review"),
    path("clear_reviews/<int:game_id>/", views.delete_reviews, name="delete_reviews"),
    path(
        "get_game_reviews/<int:game_id>/",
        views.get_game_reviews,
        name="get_game_reviews",
    ),
    path(
        "edit_review/<int:game_id>/",
        views.edit_review,
        name="edit_review",
    ),
    path("upcoming_games/", views.upcoming_games, name="upcoming_games"),
    path("toggle_game_queue/", views.toggle_game_queue, name="toggle_game_queue"),
    path("game_queue/", views.game_queue, name="game_queue"),
    path("game_queue/<int:user_id>/", views.game_queue, name="game_queue_with_id"),
    path("user_reviews/", views.user_reviews, name="user_reviews"),
    path(
        "user_reviews/<int:user_id>/", views.user_reviews, name="user_reviews_with_id"
    ),
    path("increment_likes/", views.like_review, name="like"),
    path("decrement_dislikes/", views.dislike_review, name="dislike"),
    path("game/<int:game_id>/", views.view_game, name="view_game"),
    path("share_game/<int:game_id>/", views.share_game, name="share_game"),
    path("games_shared/", views.view_games_shared, name="games_shared"),
    path("delete_shared_games/", views.delete_shared_games, name="delete_shared_games"),
    path("similar_playstyles/", views.similar_playstyles, name="similar_playstyles"),
    path("play_histories/", views.play_histories, name="play_histories"),
    path("view_franchises/", views.view_franchises, name="view_franchises"),
    path("franchise/<int:franchise_id>/", views.franchise, name="franchise"),
    path("search/franchises/", views.search_franchises, name="search_franchises"),
    path(
        "autocomplete/franchises/",
        views.autocomplete_franchises,
        name="autocomplete_franchises",
    ),
    path("characters/", views.view_characters, name="characters"),
    path("character/<int:character_id>/", views.game_character, name="character"),
    path("search/characters/", views.search_characters, name="search_characters"),
    path(
        "autocomplete/characters/",
        views.autocomplete_characters,
        name="autocomplete_characters",
    ),
    path(
        "singleplayer-games/", views.view_singleplayer_games, name="singleplayer_games"
    ),
    path("multiplayer-games/", views.view_multiplayer_games, name="multiplayer_games"),
    path("game-library/", views.game_library, name="game_library"),
    path("news/", views.latest_news, name="latest_news"),
    path("similar-games/<int:game_guid>/", views.similar_games, name="similar_games"),
    path(
        "similar-games-directory/",
        views.similar_games_directory,
        name="similar_games_directory",
    ),
    path("open-world-games/", views.open_world_games, name="open_world_games"),
    path(
        "linear-gameplay-games/",
        views.linear_gameplay_games,
        name="linear_gameplay_games",
    ),
    path("steam-games/", views.steam_games, name="steam_games"),
    path("indie-games/", views.indie_games, name="indie_games"),
    path("free-to-play-games", views.free_to_play_games, name="free_to_play_games"),
    path("vr-games", views.vr_games, name="vr_games"),
    path("beginner-games", views.beginner_games, name="beginner_games"),
    path("create-game-list/", views.create_game_list, name="create_game_list"),
    path("game-list-detail/<int:pk>/", views.game_list_detail, name="game_list_detail"),
    path("share-game-list/<int:pk>", views.share_game_list, name="share_game_list"),
    path("game-lists/<int:user_id>", views.user_game_lists, name="user_game_lists"),
    path("edit-game-list/<int:pk>/", views.edit_game_list, name="edit_game_list"),
    path("delete-game-list/<int:pk>/", views.delete_game_list, name="delete_game_list"),
    path(
        "delete-all-game-lists",
        views.delete_all_game_lists,
        name="delete_all_game_lists",
    ),
    path("shared-game-lists/", views.shared_game_lists, name="shared_game_lists"),
    path("like-game-list/<int:list_id>/", views.like_game_list, name="like_game_list"),
    path(
        "create-review/<int:game_list_id>/",
        views.review_game_list,
        name="review_game_list",
    ),
    path(
        "edit-review/<int:review_id>/",
        views.edit_game_list_review,
        name="edit_game_list_review",
    ),
    path(
        "delete-review/<int:review_id>/",
        views.delete_game_list_review,
        name="delete_game_list_review",
    ),
    path(
        "like-list-review/<int:review_id>",
        views.like_game_list_review,
        name="like_list_review",
    ),
    path(
        "reviewed-game-lists/<int:user_id>/",
        views.reviewed_game_lists,
        name="reviewed_game_lists_with_id",
    ),
    path("reviewed-game-lists/", views.reviewed_game_lists, name="reviewed_game_lists"),
    path(
        "privacy/settings/",
        views.privacy_settings,
        name="privacy_settings",
    ),
    path("explore-game-lists", views.explore_game_lists, name="explore_game_lists"),
    path(
        "delete-list-comment/<int:comment_id>/",
        views.delete_list_comment,
        name="delete_list_comment",
    ),
    path(
        "edit-comment/<int:comment_id>/",
        views.edit_list_comment,
        name="edit_list_comment",
    ),
    path(
        "post-comment/<int:game_list_id>/",
        views.post_list_comment,
        name="post_list_comment",
    ),
    path(
        "like-list-comment/<int:comment_id>",
        views.like_game_list_comment,
        name="like_list_comment",
    ),
    path(
        "toggle-favorite-game-list/<int:game_list_id>/",
        views.toggle_favorite_game_list,
        name="toggle_favorite_game_list",
    ),
    path(
        "favorite-game-lists/<int:user_id>/",
        views.favorite_game_lists,
        name="favorite_game_lists",
    ),
    path("popular_games/", views.popular_games, name="popular_games"),
    path("polls/new/", views.create_poll, name="create_poll"),
    path("polls/<int:id>/vote/", views.vote, name="vote"),
    path("polls/community/", views.community_polls, name="community_polls"),
]
