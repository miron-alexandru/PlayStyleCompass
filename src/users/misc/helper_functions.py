"""This module contains helper functions used in the users app."""

from ..models import FriendList


def are_friends(user1, user2):
    """Function to check if two users are friends."""
    friend_list_user1, created = FriendList.objects.get_or_create(user=user1)
    friend_list_user2, created = FriendList.objects.get_or_create(user=user2)

    return friend_list_user1.is_friend(user2) and friend_list_user2.is_friend(user1)
