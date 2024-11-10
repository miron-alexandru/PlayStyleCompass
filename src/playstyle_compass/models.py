"""Defines models."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator


class UserPreferences(models.Model):
    """Represents user-specific gaming preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    gaming_history = models.TextField(blank=True)
    favorite_genres = models.CharField(max_length=255, blank=True)
    platforms = models.CharField(max_length=255, blank=True)
    themes = models.CharField(max_length=255, blank=True)
    favorite_games = models.CharField(max_length=255, blank=True)
    game_queue = models.CharField(max_length=255, blank=True)
    quiz_recommendations = models.CharField(max_length=255, blank=True)
    connection_types = models.CharField(max_length=255, blank=True)
    game_styles = models.CharField(max_length=255, blank=True)

    show_in_queue = models.BooleanField(default=True)
    show_reviews = models.BooleanField(default=True)
    show_favorites = models.BooleanField(default=True)
    show_game_list_reviews = models.BooleanField(default=True)

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
    guid = models.CharField(max_length=100, unique=True)
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
    dlcs = models.CharField(max_length=200)
    franchises = models.CharField(max_length=200)
    videos = models.TextField()
    concepts = models.CharField(max_length=200)
    is_casual = models.BooleanField(default=False)
    pc_req_min = models.TextField(default="")
    pc_req_rec = models.TextField(default="")
    mac_req_min = models.TextField(default="")
    mac_req_rec = models.TextField(default="")
    linux_req_min = models.TextField(default="")
    linux_req_rec = models.TextField(default="")
    average_score = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    translated_description_ro = models.TextField(blank=True, null=True)
    translated_overview_ro = models.TextField(blank=True, null=True)

    def update_score(self):
        reviews = self.review_set.all()
        self.total_reviews = reviews.count()
        self.average_score = reviews.aggregate(Avg("score"))["score__avg"] or 0
        self.save()

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = "Games"
        ordering = ["title"]


class SharedGame(models.Model):
    """Represents a game shared between users."""

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_games"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_games",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_receiver = models.BooleanField(default=False)
    game_id = models.BigIntegerField()

    def __str__(self):
        return f"SharedGame from {self.sender} to {self.receiver}"

    class Meta:
        db_table = "Message"


class Review(models.Model):
    """Represents a review for a game."""

    SCORE_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, to_field="guid")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    reviewers = models.CharField(max_length=25)
    review_deck = models.CharField(max_length=50)
    review_description = models.TextField()
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    liked_by = models.TextField(blank=True, default="")
    disliked_by = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.game.update_score()

    def delete(self, *args, **kwargs):
        game = self.game
        super().delete(*args, **kwargs)

        game.update_score()

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


class Franchise(models.Model):
    """Represents a franchise."""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    overview = models.TextField()
    games = models.CharField(max_length=200)
    image = models.TextField()
    images = models.TextField()
    games_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Franchise: {self.title}"

    def update_games_count(self):
        games_list = self.games.split(",")
        self.games_count = len(games_list)
        self.save()

    class Meta:
        db_table = "Franchises"
        ordering = ["title", "games_count"]


class Character(models.Model):
    """Represents a character."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    deck = models.TextField()
    description = models.TextField()
    birthday = models.TextField()
    friends = models.TextField()
    enemies = models.TextField()
    games = models.TextField()
    first_game = models.CharField(max_length=50)
    franchises = models.TextField()
    image = models.TextField()
    images = models.TextField()
    character_id = models.IntegerField(default=0)

    def __str__(self):
        return f"Character: {self.name}"

    class Meta:
        db_table = "Characters"
        ordering = ["name"]


class GameModes(models.Model):
    """Represents a game that is tied to a certain game mode."""

    id = models.BigAutoField(primary_key=True)
    game_id = models.CharField(max_length=100)
    game_name = models.CharField(max_length=100)
    game_mode = models.CharField(max_length=100)

    class Meta:
        db_table = "GameModes"

    def __str__(self):
        return f"{self.game_name} - {self.game_mode}"


class News(models.Model):
    """Represents a News object."""

    id = models.BigAutoField(primary_key=True)
    article_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    url = models.URLField()
    image = models.URLField()
    publish_date = models.CharField(max_length=50)
    platforms = models.CharField(max_length=255)

    class Meta:
        db_table = "News"

    def __str__(self):
        return f"Article: {self.title}"


class GameList(models.Model):
    """Represents a game list."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="game_lists"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    game_guids = models.JSONField(default=list)
    additional_games = models.JSONField(default=list)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="shared_game_lists"
    )
    shared_by = models.JSONField(default=dict, blank=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="liked_game_lists"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def like_count(self):
        """Returns the total number of likes for the game list."""
        return self.liked_by.count()

    def __str__(self):
        return self.title

    @property
    def share_count(self):
        """Returns the number of users the game list is shared with."""
        return self.shared_with.count()

    @property
    def total_games(self):
        """Returns the total number of games in the list."""
        return len(self.game_guids) + len(self.additional_games)

    @property
    def review_count(self):
        """Returns the total number of reviews for the game list."""
        return self.reviews.count()


class ListReview(models.Model):
    """Model to store user reviews and ratings for game lists."""

    game_list = models.ForeignKey(
        "GameList", on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.CharField(max_length=255, blank=False)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 (worst) and 5 (best)",
    )
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_reviews",
        blank=True,
    )

    class Meta:
        unique_together = ("game_list", "user")

    def __str__(self):
        return f"Review by {self.user} on {self.game_list}"

    @property
    def like_count(self):
        """Returns the number of likes."""
        return self.liked_by.count()
