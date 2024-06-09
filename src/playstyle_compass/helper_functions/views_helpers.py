"""
The 'views_helpers' module contains the recommendation engine and 
other helper functions used for differend views."""

from datetime import date, datetime
from collections import defaultdict
from fuzzywuzzy import fuzz

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from ..models import Game, Review, Franchise
from users.models import FriendList


class RecommendationEngine:
    """Class to process user preferences and generate game recommendations."""

    def __init__(self, request, user_preferences):
        """Initialize the RecommendationEngine class."""
        self.request = request
        self.user_preferences = user_preferences
        self.matching_games = self.initialize_matching_games()
        self.current_date = date.today()

    def find_matching_title_games(self, history_game):
        """Find games with titles similar to the given history game."""
        games = Game.objects.all()
        matches = []

        for game in games:
            similarity = fuzz.ratio(history_game.lower(), game.title.lower())
            if similarity > 65:
                matches.append(game)

        return matches

    def find_matching_genre_games(self, matching_game):
        """Find games with genres matching the given game."""
        if matching_game.genres:
            return Game.objects.filter(genres__icontains=matching_game.genres)
        return []

    def parse_release_date(self, release_date_str):
        """Parse a release date string into a datetime.date object."""
        try:
            return datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            return datetime.strptime(release_date_str + "-01-01", "%Y-%m-%d").date()

    def process_gaming_history(self, gaming_history):
        """Process the user's gaming history to find matching games and genres."""
        unique_games = set()
        unique_genres = set()
        games_to_exclude = set()

        for history_game in gaming_history:
            matching_title_games = self.find_matching_title_games(history_game)

            for matching_game in matching_title_games:
                if matching_game not in unique_games:
                    unique_games.add(matching_game)
                    unique_genres.add(matching_game.genres)

                    matching_genre_games = self.find_matching_genre_games(matching_game)

                    for genre_game in matching_genre_games:
                        if genre_game not in self.matching_games["gaming_history"]:
                            self.matching_games["gaming_history"].append(genre_game)

                        release_date = self.parse_release_date(genre_game.release_date)

                        if release_date >= self.current_date:
                            games_to_exclude.add(genre_game)

        self.matching_games["gaming_history"] = [
            game
            for game in self.matching_games["gaming_history"]
            if game not in games_to_exclude
        ]

    def apply_filters(self, genres, themes, platforms):
        """Apply genre and platform filters to matching games."""
        genre_filters = Q()
        theme_filters = Q()
        platform_filters = Q()

        for genre in genres:
            genre_filters |= Q(genres__icontains=genre)

        for theme in themes:
            theme_filters |= Q(themes__icontains=theme)

        for platform in platforms:
            platform_filters |= Q(platforms__icontains=platform)

        common_filters = genre_filters & platform_filters
        upcoming_filter = Q(release_date__gte=self.current_date)

        self.matching_games["favorite_genres"] = Game.objects.filter(
            genre_filters
        ).exclude(upcoming_filter)
        self.matching_games["themes"] = Game.objects.filter(theme_filters).exclude(
            upcoming_filter
        )
        self.matching_games["common_genres_platforms"] = Game.objects.filter(
            common_filters
        ).exclude(upcoming_filter)
        self.matching_games["preferred_platforms"] = Game.objects.filter(
            platform_filters
        ).exclude(upcoming_filter)

    def process_user_data(self):
        """Process user preferences, gaming history, and apply filters."""
        favorite_genres = [
            genre.strip() for genre in self.user_preferences.favorite_genres.split(",")
        ]
        themes = [theme.strip() for theme in self.user_preferences.themes.split(",")]
        preferred_platforms = [
            platform.strip() for platform in self.user_preferences.platforms.split(",")
        ]
        gaming_history = [
            game.strip() for game in self.user_preferences.gaming_history.split(",")
        ]

        self.process_gaming_history(gaming_history)

    def filter_preferences(self):
        """Filter matching games based on user preferences."""
        favorite_genres = [
            genre.strip() for genre in self.user_preferences.favorite_genres.split(",")
        ]
        themes = [theme.strip() for theme in self.user_preferences.themes.split(",")]
        preferred_platforms = [
            platform.strip() for platform in self.user_preferences.platforms.split(",")
        ]

        self.apply_filters(favorite_genres, themes, preferred_platforms)

    def initialize_matching_games(self):
        """Initialize a dictionary to store matching games in different categories."""
        return {
            "gaming_history": [],
            "favorite_genres": [],
            "themes": [],
            "preferred_platforms": [],
            "common_genres_platforms": [],
        }

    def sort_matching_games(self):
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
        self.process_user_data()
        self.filter_preferences()
        self.sort_matching_games()


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
    total_similarity_score = sum(
        calculate_similarity(
            set(getattr(user1, pref).split(",")),
            set(getattr(user2, pref).split(",")),
        )
        for pref in preferences
    )
    return total_similarity_score / len(preferences)


def paginate_objects(request, objects):
    """Function to paginate objects."""
    objects_per_page = 10

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
            genres.update(game.genres.split(','))
        if game.concepts:
            concepts.update(game.concepts.split(','))
        if game.themes:
            themes.update(game.themes.split(','))
        if game.platforms:
            platforms.update(game.platforms.split(','))
        if game.franchises:
            franchises.update(game.franchises.split(','))

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
        'genres': request.GET.getlist('genres'),
        'concepts': request.GET.getlist('concepts'),
        'themes': request.GET.getlist('themes'),
        'platforms': request.GET.getlist('platforms'),
        'franchises': request.GET.getlist('franchises')
    }

def sort_game_library(games, sort_by):
    """Sort game library based on the sorting option."""
    if sort_by == 'release_date_asc':
        return games.order_by('release_date')
    elif sort_by == 'release_date_desc':
        return games.order_by('-release_date')
    elif sort_by == 'title_asc':
        return games.order_by('title')
    elif sort_by == 'title_desc':
        return games.order_by('-title')
    elif sort_by == 'average_score_asc':
        return games.order_by('average_score')
    elif sort_by == 'average_score_desc':
        return games.order_by('-average_score')
    else:
        return games
