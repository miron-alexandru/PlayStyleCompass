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
        self.matching_games["themes"] = Game.objects.filter(
            theme_filters
        ).exclude(upcoming_filter)
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
        themes = [
            theme.strip() for theme in self.user_preferences.themes.split(",")
        ]
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
        themes = [
            theme.strip() for theme in self.user_preferences.themes.split(",")
        ]
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
            "recommended": None,
        }

        sort_key_function = sorting_functions.get(sort_option)
        if sort_key_function:
            for category, game_list in self.matching_games.items():
                self.matching_games[category] = sorted(game_list, key=sort_key_function)
                if sort_option == "release_date_desc":
                    self.matching_games[category] = list(
                        reversed(self.matching_games[category])
                    )

    def process(self):
        """Execute the recommendation."""
        self.process_user_data()
        self.filter_preferences()
        self.sort_matching_games()


def calculate_game_scores(games):
    """Calculate average scores and total reviews for games."""
    for game in games:
        game_reviews = Review.objects.filter(game_id=game.guid)
        total_score = 0

        total_score = sum(int(review.score) for review in game_reviews)
        average_score = total_score / len(game_reviews) if game_reviews else 0
        total_reviews = len(game_reviews)

        game.average_score = average_score
        game.total_reviews = total_reviews

    return games


def calculate_single_game_score(game):
    """Calculate average score and total reviews for a single game."""
    game_reviews = Review.objects.filter(game_id=game.guid)
    total_score = sum(int(review.score) for review in game_reviews)

    average_score = total_score / len(game_reviews) if game_reviews else 0
    total_reviews = len(game_reviews)

    game.average_score = average_score
    game.total_reviews = total_reviews

    return game


def paginate_matching_games_dict(request, matching_games):
    """Function to paginate games and calculate average scores."""
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

        page = calculate_game_scores(page)

    return paginated_games


def paginate_matching_games_query(request, matching_games):
    """Function to paginate games and calculate average scores."""
    games_per_page = 10

    paginator = Paginator(matching_games, games_per_page)
    page_number = request.GET.get("page", 1)

    try:
        paginated_games = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        paginated_games = paginator.page(1)

    paginated_games = calculate_game_scores(paginated_games)

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
