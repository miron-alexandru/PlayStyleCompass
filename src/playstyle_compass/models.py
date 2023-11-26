"""Defines models."""

from django.db import models
from django.contrib.auth.models import User


class GamingPreferences(models.Model):
    """Represents a user's gaming preferences."""

    id = models.BigAutoField(primary_key=True)
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.text)


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

    def __str__(self):
        return self.user.username


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


    def __str__(self):
        return f"Review by {self.reviewers} for {self.game.title}"

    class Meta:
        db_table = "Reviews"
