"""This module contains helper functions used in the users app."""

from ..models import FriendList
from django.utils import timezone
from datetime import timedelta


def are_friends(user1, user2):
    """Function to check if two users are friends."""
    friend_list_user1, created = FriendList.objects.get_or_create(user=user1)
    friend_list_user2, created = FriendList.objects.get_or_create(user=user2)

    return friend_list_user1.is_friend(user2) and friend_list_user2.is_friend(user1)


def check_quiz_time(user):
    """Check if the user can take the quiz."""
    if last_update_time := user.userprofile.quiz_taken_date:
        one_day_ago = timezone.now() - timedelta(days=1)
        if last_update_time > one_day_ago:
            time_remaining = (last_update_time - one_day_ago).total_seconds()
            return int(time_remaining) // 3600, int((time_remaining % 3600) // 60)
    return None, None
