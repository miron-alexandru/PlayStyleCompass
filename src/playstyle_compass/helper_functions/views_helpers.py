"""
The 'views_helpers' module contains the recommendation engine and 
other helper functions used for differend views."""

import re
from datetime import date, datetime
from collections import defaultdict
from operator import itemgetter
from fuzzywuzzy import fuzz

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from playstyle_compass.models import UserPreferences, Game, Review, Franchise
from users.models import FriendList


class RecommendationEngine:
    """Class to process user preferences and generate game recommendations."""

    def __init__(self, request, user_preferences):
        """Initialize the RecommendationEngine class."""
        self.request = request
        self.user_preferences = user_preferences
        self.matching_games = self._initialize_matching_games()
        self.current_date = date.today()
        self.games = Game.objects.all()

    def _find_matching_title_games(self, history_game):
        """Find games with titles similar to the given history game."""
        history_game_lower = history_game.lower()

        return [
            game
            for game in self.games
            if fuzz.ratio(history_game_lower, game.title.lower()) > 65
        ]

    def _find_matching_genre_games(self, matching_game):
        """Find games with genres matching the given game."""
        if matching_game.genres:
            return Game.objects.filter(genres__icontains=matching_game.genres)
        return []

    def _parse_release_date(self, release_date_str):
        if not release_date_str or release_date_str == '0000':
            return None  # or some default date
        try:
            # if only year is stored
            if len(release_date_str) == 4:
                return datetime.strptime(release_date_str + "-01-01", "%Y-%m-%d").date()
            else:
                return datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _process_gaming_history(self, gaming_history):
        """Process the user's gaming history to find matching games and genres."""
        unique_games, unique_genres, games_to_exclude = set(), set(), set()

        def process_game(matching_game):
            unique_games.add(matching_game)
            unique_genres.update(matching_game.genres)
            matching_genre_games = self._find_matching_genre_games(matching_game)

            for genre_game in matching_genre_games:
                if genre_game not in self.matching_games["gaming_history"]:
                    self.matching_games["gaming_history"].append(genre_game)

                release_date = self._parse_release_date(genre_game.release_date)
                if release_date is not None and release_date >= self.current_date:
                    games_to_exclude.add(genre_game)

        for history_game in gaming_history:
            matching_title_games = self._find_matching_title_games(history_game)
            for matching_game in matching_title_games:
                if matching_game not in unique_games:
                    process_game(matching_game)

        # Remove excluded games from the final list
        self.matching_games["gaming_history"] = [
            game
            for game in self.matching_games["gaming_history"]
            if game not in games_to_exclude
        ]

    def _apply_filters(self, genres, themes, platforms, game_styles, connection_types):
        """Apply filters to matching games."""

        def apply_filter(filter_conditions):
            """Helper function to apply filter conditions and exclude upcoming games."""
            return Game.objects.filter(filter_conditions).exclude(upcoming_filter)

        def calculate_recommendation_score(game):
            """Helper function to calculate recommendation score for a game."""

            score = 0

            if game.genres:
                if any(genre in game.genres for genre in genres):
                    score += WEIGHTS["genre"]

            if game.themes:
                if any(theme in game.themes for theme in themes):
                    score += WEIGHTS["theme"]

            if game.platforms:
                if any(platform in game.platforms for platform in platforms):
                    score += WEIGHTS["platform"]

            if game.concepts:
                if any(game_style in game.concepts for game_style in game_styles):
                    score += WEIGHTS["game_style"]

            if game.concepts:
                if any(
                    connection_type in game.concepts
                    for connection_type in connection_types
                ):
                    score += WEIGHTS["connection_type"]

            return score

        genre_filters = Q()
        theme_filters = Q()
        platform_filters = Q()
        game_style_filters = Q()
        connection_type_filters = Q()

        # Define weight for each category in the recommendation system
        WEIGHTS = {
            "genre": 3,
            "theme": 1,
            "platform": 3,
            "game_style": 1,
            "connection_type": 1,
        }

        # Build Q objects for filtering
        for genre in genres:
            genre_filters |= Q(genres__icontains=genre)

        for theme in themes:
            theme_filters |= Q(themes__icontains=theme)

        for platform in platforms:
            platform_filters |= Q(platforms__icontains=platform)

        for game_style in game_styles:
            game_style_filters |= Q(concepts__icontains=game_style)

        if "Online" in connection_types:
            connection_type_filters |= Q(concepts__icontains="Online")
        else:
            connection_type_filters &= ~Q(concepts__icontains="Online")

        for connection_type in connection_types:
            if connection_type != "Online":
                connection_type_filters |= Q(concepts__icontains=connection_type)

        common_filters = genre_filters & platform_filters
        upcoming_filter = Q(release_date__gte=self.current_date)

        self.matching_games.update(
            {
                "favorite_genres": apply_filter(genre_filters),
                "themes": apply_filter(theme_filters),
                "common_genres_platforms": apply_filter(common_filters),
                "preferred_platforms": apply_filter(platform_filters),
                "game_styles": apply_filter(game_style_filters),
                "connection_types": apply_filter(connection_type_filters),
            }
        )

        # Pre-filter games before applying the recommendation algorithm
        pre_filtered_games = Game.objects.filter(
            genre_filters | theme_filters | platform_filters
        ).exclude(upcoming_filter)

        game_scores = defaultdict(int)

        for game in pre_filtered_games:
            # Calculate the recommendation score for each game
            game_scores[game] = calculate_recommendation_score(game)

        playstyle_games = sorted(game_scores.items(), key=itemgetter(1), reverse=True)

        # Add the recommended games to the matching games with a score threshold
        self.matching_games["playstyle_games"] = [
            game for game, score in playstyle_games if score > 6
        ]

    def _process_user_data(self):
        """Process user gaming history and apply filters."""
        gaming_history = [
            game.strip() for game in self.user_preferences.gaming_history.split(",")
        ]

        self._process_gaming_history(gaming_history)

    def _filter_preferences(self):
        """Filter matching games based on user preferences."""
        favorite_genres = [
            genre.strip() for genre in self.user_preferences.favorite_genres.split(",")
        ]
        themes = [theme.strip() for theme in self.user_preferences.themes.split(",")]
        preferred_platforms = [
            platform.strip() for platform in self.user_preferences.platforms.split(",")
        ]
        game_styles = [
            game_style.strip()
            for game_style in self.user_preferences.game_styles.split(",")
        ]
        connection_types = [
            connection_type.strip()
            for connection_type in self.user_preferences.connection_types.split(",")
        ]

        self._apply_filters(
            favorite_genres, themes, preferred_platforms, game_styles, connection_types
        )

    def _initialize_matching_games(self):
        """Initialize a dictionary to store matching games in different categories."""
        return {
            "gaming_history": [],
            "favorite_genres": [],
            "themes": [],
            "preferred_platforms": [],
            "common_genres_platforms": [],
            "game_styles": [],
            "connection_types": [],
        }

    def _sort_matching_games(self):
        """Sort matching games based on a specified sorting option."""
        sort_option = self.request.GET.get("sort", "recommended")
        sorting_functions = {
            "release_date_asc": lambda game: game.release_date,
            "release_date_desc": lambda game: game.release_date,
            "title_asc": lambda game: game.title.lower(),
            "title_desc": lambda game: game.title.lower(),
            "score_asc": lambda game: game.average_score,
            "score_desc": lambda game: game.average_score,
            "recommended": None,
        }

        sort_key_function = sorting_functions.get(sort_option)
        if sort_key_function:
            for category, game_list in self.matching_games.items():

                sorted_game_list = sorted(game_list, key=sort_key_function)
                if sort_option in ["release_date_desc", "title_desc", "score_desc"]:
                    sorted_game_list = list(reversed(sorted_game_list))

                self.matching_games[category] = sorted_game_list

    def process(self):
        """Execute the recommendation."""
        self._process_user_data()
        self._filter_preferences()
        self._sort_matching_games()


def paginate_matching_games(request, matching_games):
    """Function to paginate games and calculate average scores."""
    games_per_page = 10
    paginated_games = defaultdict(list)

    if isinstance(matching_games, dict):
        for category, game_list in matching_games.items():
            paginator = Paginator(game_list, games_per_page)
            page_number = request.GET.get(f"{category}_page", 1)

            try:
                page = paginator.page(page_number)
            except (PageNotAnInteger, EmptyPage):
                page = paginator.page(1)

            paginated_games[category] = page
    else:
        paginator = Paginator(matching_games, games_per_page)
        page_number = request.GET.get("page", 1)

        try:
            paginated_games = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            paginated_games = paginator.page(1)

    return paginated_games


def get_friend_list(user):
    friends_list, created = FriendList.objects.get_or_create(user=user)
    user_friends = friends_list.friends.all()

    return user_friends


def calculate_similarity(set1, set2):
    """Function used to calculate Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity_score = intersection / union if union > 0 else 0

    return similarity_score


def calculate_average_similarity(user1, user2, preferences):
    """Function used to calculate average similarity across multiple preferences"""
    if not preferences:
        return 0.0

    total_similarity_score = sum(
        calculate_similarity(
            set(getattr(user1, pref).split(",")),
            set(getattr(user2, pref).split(",")),
        )
        for pref in preferences
    )
    return total_similarity_score / len(preferences)


def paginate_objects(request, objects, objects_per_page=10):
    """Function to paginate objects."""

    paginator = Paginator(objects, objects_per_page)
    page_number = request.GET.get("page", 1)

    try:
        paginated_objects = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        paginated_objects = paginator.page(1)

    return paginated_objects


def gather_game_attributes(games):
    """Gather unique game attributes for filtering."""
    genres, concepts, themes, platforms, franchises = set(), set(), set(), set(), set()

    for game in games:
        if game.genres:
            genres.update(game.genres.split(","))
        if game.concepts:
            concepts.update(game.concepts.split(","))
        if game.themes:
            themes.update(game.themes.split(","))
        if game.platforms:
            platforms.update(game.platforms.split(","))
        if game.franchises:
            franchises.update(game.franchises.split(","))

    return genres, concepts, themes, platforms, franchises


def build_query(selected_filters):
    """Build query based on the selected filters."""
    query = Q()

    for filter_type, selected_items in selected_filters.items():
        if selected_items and any(selected_items):
            filter_query = Q()
            for item in selected_items:
                filter_query |= Q(**{f"{filter_type}__icontains": item})
            query |= filter_query

    return query


def get_selected_filters(request):
    """Get the selected filters from the request."""
    return {
        "genres": request.GET.getlist("genres"),
        "concepts": request.GET.getlist("concepts"),
        "themes": request.GET.getlist("themes"),
        "platforms": request.GET.getlist("platforms"),
        "franchises": request.GET.getlist("franchises"),
    }


def sort_game_library(games, sort_by):
    """Sort game library based on the sorting option."""
    if sort_by == "release_date_asc":
        return games.order_by("release_date")
    elif sort_by == "release_date_desc":
        return games.order_by("-release_date")
    elif sort_by == "title_asc":
        return games.order_by("title")
    elif sort_by == "title_desc":
        return games.order_by("-title")
    elif sort_by == "average_score_asc":
        return games.order_by("average_score")
    elif sort_by == "average_score_desc":
        return games.order_by("-average_score")
    else:
        return games


def get_user_context(request):
    """Return user context used in a similar way for similar views."""
    user = request.user if request.user.is_authenticated else None
    user_preferences = get_object_or_404(UserPreferences, user=user) if user else None
    user_friends = get_friend_list(user) if user else []

    return user, user_preferences, user_friends


def get_associated_platforms(articles):
    """Get unique platforms from articles for filtering."""
    platforms = set()

    for article in articles:
        if article.platforms:
            cleaned_platforms = [
                platform.strip() for platform in article.platforms.split(",")
            ]
            platforms.update(cleaned_platforms)

    return platforms


def sort_articles(articles, sort_by):
    """Sort articles based on the sorting option."""
    if sort_by == "publish_date_asc":
        return articles.order_by("publish_date")
    elif sort_by == "publish_date_desc":
        return articles.order_by("-publish_date")
    elif sort_by == "title_asc":
        return articles.order_by("title")
    elif sort_by == "title_desc":
        return articles.order_by("-title")
    else:
        return articles


def safe_split(value):
    return set(value.split(",")) if value else set()


def get_similar_games(game, min_matching_attributes=3):
    """Find games similar to the given game based on shared attributes."""

    # Extract and clean the attributes of the main game, converting them into sets for easy comparison
    attributes = {
        "genres": safe_split(game.genres),
        "themes": safe_split(game.themes),
        "concepts": safe_split(game.concepts),
        "platforms": safe_split(game.platforms),
        "developers": safe_split(game.developers),
    }

    def count_matching_attributes(other_game):
        """Count how many attributes of the other_game match with the main game's attributes."""
        # Extract and clean the attributes of the other game
        game_attributes = {
            "genres": safe_split(other_game.genres),
            "themes": safe_split(other_game.themes),
            "concepts": safe_split(other_game.concepts),
            "platforms": safe_split(other_game.platforms),
            "developers": safe_split(other_game.developers),
        }

        match_count = 0

        # Iterate over each attribute type and check for intersections
        for attr, values in attributes.items():
            if values & game_attributes[attr]:  # Check if there is any common attribute
                match_count += 1

        return match_count

    # Query all games from the database excluding the main game itself
    all_games = Game.objects.exclude(guid=game.guid)

    # Filter games to find those with at least the specified number of matching attributes
    matching_games = []
    for g in all_games:
        if count_matching_attributes(g) >= min_matching_attributes:
            matching_games.append(g)

    return matching_games


def get_first_letter(title):
    """Extracts the first alphabetical character from a title, skipping numbers."""
    match = re.search(r"[a-zA-Z]", title)
    return match.group(0).upper() if match else "#"
