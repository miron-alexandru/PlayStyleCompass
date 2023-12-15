"""Defines models."""

from django.db import models
from django.contrib.auth.models import User



class UserPreferences(models.Model):
    """Represents user-specific gaming preferences."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gaming_history = models.TextField(blank=True)
    favorite_genres = models.CharField(max_length=255, blank=True)
    platforms = models.CharField(max_length=255, blank=True)
    favorite_games = models.CharField(max_length=255, blank=True)
    game_queue = models.CharField(max_length=255, blank=True)

    def add_favorite_game(self, game_id):
        """Add a game to favorites."""
        favorite_games_list = self.favorite_games.split(",")
        if str(game_id) not in favorite_games_list:
            favorite_games_list.append(str(game_id))
            self.favorite_games = ",".join(favorite_games_list)
            self.save()

    def remove_favorite_game(self, game_id):
        """Remove a game from favorites."""
        favorite_games_list = self.favorite_games.split(",")
        if str(game_id) in favorite_games_list:
            favorite_games_list.remove(str(game_id))
            self.favorite_games = ",".join(favorite_games_list)
            self.save()

    def get_favorite_games(self):
        """Get the favorite games."""
        favorite_games_list = self.favorite_games.split(",")
        favorite_games_ids = [
            int(game_id.strip()) for game_id in favorite_games_list if game_id.strip()
        ]
        return favorite_games_ids

    def add_game_to_queue(self, game_id):
        """Add a game to queue."""
        game_queue_list = self.game_queue.split(",")
        if str(game_id) not in game_queue_list:
            game_queue_list.append(str(game_id))
            self.game_queue = ",".join(game_queue_list)
            self.save()

    def remove_game_from_queue(self, game_id):
        """Remove a game from queue."""
        game_queue_list = self.game_queue.split(",")
        if str(game_id) in game_queue_list:
            game_queue_list.remove(str(game_id))
            self.game_queue = ",".join(game_queue_list)
            self.save()

    def get_game_queue(self):
        """Get games queue."""
        game_queue_list = self.game_queue.split(",")
        game_queue_ids = [
            int(game_id.strip()) for game_id in game_queue_list if game_id.strip()
        ]
        return game_queue_ids

    def get_list_length(self, attribute):
        if getattr(self, attribute):
            elements = [
                element
                for element in getattr(self, attribute).split(",")
                if element.strip()
            ]
            return len(elements)
        return 0

    def get_favorite_games_number(self):
        return self.get_list_length("favorite_games")

    def get_game_queue_number(self):
        return self.get_list_length("game_queue")

    def __str__(self):
        return f"{self.user}'s user preferences"


class Game(models.Model):
    """Represents a game."""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    overview = models.TextField()
    genres = models.CharField(max_length=200)
    platforms = models.CharField(max_length=200)
    themes = models.CharField(max_length=200)
    image = models.TextField()
    release_date = models.CharField(max_length=100)
    developers = models.CharField(max_length=100)
    game_images = models.TextField()
    similar_games = models.CharField(max_length=200)

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = "Games"
        ordering = ["title"]


class Review(models.Model):
    """Represents a review for a game."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewers = models.CharField(max_length=25)
    review_deck = models.CharField(max_length=50)
    review_description = models.TextField()
    SCORE_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    liked_by = models.TextField(blank=True, default="")
    disliked_by = models.TextField(blank=True, default="")

    def add_like(self, user_id):
        """Add a like to the review."""
        if not self.user_has_liked(user_id):
            self.liked_by += f"{user_id},"
            self.likes += 1
            self.save()

    def remove_like(self, user_id):
        """Remove a like from the review.."""
        liked_by_list = self.liked_by.split(",")
        if str(user_id) in liked_by_list:
            liked_by_list.remove(str(user_id))
            self.liked_by = ",".join(liked_by_list)
            self.likes -= 1
            self.save()

    def user_has_liked(self, user_id):
        """Check if the user has already liked the review."""
        liked_by = self.liked_by
        if liked_by is not None:
            return str(user_id) in liked_by.split(",")
        return False

    def add_dislike(self, user_id):
        """Add a dislike to the review."""
        if not self.user_has_disliked(user_id):
            self.disliked_by += f"{user_id},"
            self.dislikes += 1
            self.save()

    def remove_dislike(self, user_id):
        """Remove a dislike from the review."""
        disliked_by_list = self.disliked_by.split(",")
        if str(user_id) in disliked_by_list:
            disliked_by_list.remove(str(user_id))
            self.disliked_by = ",".join(disliked_by_list)
            self.dislikes -= 1
            self.save()

    def user_has_disliked(self, user_id):
        """Check if the user has already disliked the review."""
        disliked_by = self.disliked_by
        if disliked_by is not None:
            return str(user_id) in disliked_by.split(",")
        return False

    def __str__(self):
        return f"Review by {self.reviewers} for {self.game.title}"

    class Meta:
        db_table = "Reviews"
