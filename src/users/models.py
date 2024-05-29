"""Defines models."""

import pytz
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    """User profile model."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    profile_name = models.CharField(max_length=15, blank=True, null=True)
    name_last_update_time = models.DateTimeField(null=True, blank=True)
    quiz_taken_date = models.DateTimeField(null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    quiz_taken = models.BooleanField(default=False)
    bio = models.CharField(max_length=50, null=True, default="", help_text="Write a short bio, up to 50 characters.")
    favorite_game = models.CharField(max_length=50, null=True, default="", help_text="Enter your favorite game, up to 50 characters.")
    favorite_character = models.CharField(max_length=50, null=True, default="", help_text="Enter your favorite game character, up to 50 characters.")
    gaming_commitment = models.CharField(
        max_length=50,
        default='Casual',
        help_text="Choose your level of commitment in gaming."
    )
    main_gaming_platform = models.CharField(
        max_length=50,
        default='PC',
        help_text="Choose your main gaming platform."
    )
    social_media = models.CharField(max_length=100, null=True, default="", help_text="Enter your social media link")



    def clean(self):
        profile_name = self.profile_name
        existing_profiles = UserProfile.objects.filter(
            profile_name=profile_name
        ).exclude(user=self.user)

        if existing_profiles.exists():
            raise ValidationError(
                "This profile name is already in use by another user. Please choose a different one."
            )

    def __str__(self):
        return self.user.username


class ContactMessage(models.Model):
    """Contact message model."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def formatted_timestamp(self):
        """Return the timestap formatted."""
        return self.timestamp.strftime("%b %d, %Y %I:%M %p")


class FriendList(models.Model):
    """Friends list model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_of"
    )
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="user_friends"
    )

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """Add a friend to the friends list."""
        if account not in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        """Remove a friend from the friends list."""
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, removee):
        """Unfriend someone from the friends list."""
        remover_friends_list = self
        remover_friends_list.remove_friend(removee)
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(remover_friends_list.user)

    def is_friend(self, account):
        """Check if an user is a friend."""
        return self.friends.filter(pk=account.id).exists()


class FriendRequest(models.Model):
    """Friend requests model."""

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender_of"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver_of"
    )
    is_active = models.BooleanField(blank=False, null=False, default=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        """Accept a friend request."""
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        sender_friend_list = FriendList.objects.get(user=self.sender)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)

        if sender_friend_list:
            sender_friend_list.add_friend(self.receiver)

    def decline(self):
        """Decline friend request."""
        self.is_active = False
        self.save()

    def cancel(self):
        """Cancel friend request."""
        self.is_active = False
        self.save()

    def delete(self):
        """Delete friend request."""
        self.is_active = False
        self.save()
        super().delete()

    def activate(self):
        """Activate a friend request."""
        self.is_active = True
        self.save()


class Message(models.Model):
    """Represents a message sent by a user to another user."""

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    title = models.TextField(max_length=30)
    message = models.TextField(max_length=3500)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_receiver = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

    class Meta:
        db_table = "UserMessages"


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.timestamp is None:
            self.timestamp = timezone.now().isoformat()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification(id={self.id}, user={self.user.username}, message='{self.message}', is_read={self.is_read}, is_active={self.is_active})"

        super().save(*args, **kwargs)


class QuizQuestion(models.Model):
    """Model used to store quiz questions."""

    name = models.CharField(max_length=100)
    question_text = models.CharField(max_length=200)
    option1 = models.CharField(max_length=150, default="")
    option2 = models.CharField(max_length=150, default="")
    option3 = models.CharField(max_length=150, default="")
    option4 = models.CharField(max_length=150, default="")

    def __str__(self):
        return f"{self.name}"


class QuizUserResponse(models.Model):
    """Model used to store responses from users to a quiz question."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    response_text = models.CharField(max_length=200, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response from {self.user} for the question {self.question.name}"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
