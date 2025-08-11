from .base import *
import json


class FriendsListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@example.com", password="StrongPass123!"
        )
        self.url = lambda uid: reverse("users:friends_list", kwargs={"user_id": uid})

    def test_redirect_if_not_logged(self):
        response = self.client.get(self.url(self.user1.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_cannot_view_others_list(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.get(self.url(self.user2.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("cannot view the friends list", response.content.decode().lower())

    def test_own_list_renders(self):
        self.client.login(username="user1", password="StrongPass123!")
        FriendList.objects.create(user=self.user1)
        response = self.client.get(self.url(self.user1.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/friends_list.html")
        self.assertEqual(response.context["this_user"], self.user1)
        self.assertIn("friends", response.context)

    def test_creates_friendlist_if_missing(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.get(self.url(self.user1.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(FriendList.objects.filter(user=self.user1).exists())


class RemoveFriendViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@example.com", password="StrongPass123!"
        )
        self.url = reverse("users:remove_friend")
        self.friend_list1 = FriendList.objects.create(user=self.user1)
        self.friend_list2 = FriendList.objects.create(user=self.user2)
        self.friend_list1.friends.add(self.user2)
        self.friend_list2.friends.add(self.user1)

    def post(self, client, data):
        return client.post(self.url, data, secure=True)

    def test_redirect_if_not_logged(self):
        response = self.post(self.client, {"receiver_user_id": self.user2.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_no_receiver_id_error(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, {})
        data = json.loads(response.content)
        self.assertIn("error", data["message"].lower())

    def test_remove_success(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, {"receiver_user_id": self.user2.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("successfully removed", data["message"].lower())
        self.assertNotIn(self.user2, self.friend_list1.friends.all())

    def test_invalid_friend_id(self):
        self.client.login(username="user1", password="StrongPass123!")
        invalid_id = self.user2.id + 999
        response = self.post(self.client, {"receiver_user_id": invalid_id})
        self.assertEqual(response.status_code, 404)


class SendFriendRequestViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@example.com", password="StrongPass123!"
        )

    def post(self, client, target_id):
        url = reverse("users:friend_request", args=[target_id])
        return client.post(url, {"user_id": target_id}, secure=True)

    def test_redirect_if_not_logged(self):
        response = self.post(self.client, self.user2.id)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_send_to_self(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, self.user1.id)
        data = json.loads(response.content)
        self.assertIn("yourself", data["message"].lower())

    def test_send_to_nonexistent_user(self):
        self.client.login(username="user1", password="StrongPass123!")
        invalid_id = self.user2.id + 999
        response = self.post(self.client, invalid_id)
        data = json.loads(response.content)
        self.assertIn("does not exist", data["message"].lower())

    def test_send_when_already_friends(self):
        FriendList.objects.create(user=self.user1).friends.add(self.user2)
        FriendList.objects.create(user=self.user2).friends.add(self.user1)
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, self.user2.id)
        data = json.loads(response.content)
        self.assertIn("already in your friends list", data["message"].lower())

    def test_send_when_request_already_exists(self):
        FriendRequest.objects.create(sender=self.user1, receiver=self.user2, is_active=True)
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, self.user2.id)
        data = json.loads(response.content)
        self.assertIn("already sent", data["message"].lower())

    def test_reactivate_inactive_request(self):
        FriendRequest.objects.create(sender=self.user1, receiver=self.user2, is_active=False)
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, self.user2.id)
        data = json.loads(response.content)
        self.assertIn("friend request sent", data["message"].lower())
        fr = FriendRequest.objects.get(sender=self.user1, receiver=self.user2)
        self.assertTrue(fr.is_active)

    def test_create_new_request(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, self.user2.id)
        data = json.loads(response.content)
        self.assertIn("friend request sent", data["message"].lower())
        self.assertTrue(
            FriendRequest.objects.filter(sender=self.user1, receiver=self.user2).exists()
        )


class CancelFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
        username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
        username="user2", email="u2@example.com", password="StrongPass123!"
        )
        self.url = reverse("users:friend_request_cancel")

    def post(self, client, receiver_id):
        return client.post(self.url, {"receiver_user_id": receiver_id}, secure=True)

    def test_redirect_if_not_logged_in(self):
        response = self.post(self.client, self.user2.id)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_cancel_nonexistent_request(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.post(self.client, self.user2.id)
        data = json.loads(response.content)
        self.assertIn("nothing to cancel", data["message"].lower())

    def test_cancel_request_success(self):
        self.client.login(username="user1", password="StrongPass123!")
        fr = FriendRequest.objects.create(sender=self.user1, receiver=self.user2, is_active=True)
        response = self.post(self.client, self.user2.id)
        data = json.loads(response.content)
        self.assertIn("friend request canceled", data["message"].lower())
        fr.refresh_from_db()
        self.assertFalse(fr.is_active)

    def test_post_without_receiver_id(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.post(self.url, {}, secure=True)
        data = json.loads(response.content)
        self.assertIn("unable to cancel", data["message"].lower())

    def test_get_method_not_allowed(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        data = json.loads(response.content)
        self.assertIn("must be authenticated", data["message"].lower())


class FriendRequestsViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
        username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
        username="user2", email="u2@example.com", password="StrongPass123!"
        )
        self.url = lambda user_id: reverse("users:friend_requests", kwargs={"user_id": user_id})


    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url(self.user1.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_cannot_view_other_users_requests(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.get(self.url(self.user2.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("You can't view the friend requests of another user.", response.content.decode())

    def test_view_own_requests_lists(self):
        self.client.login(username="user1", password="StrongPass123!")

        FriendRequest.objects.create(sender=self.user2, receiver=self.user1, is_active=True)

        FriendRequest.objects.create(sender=self.user1, receiver=self.user2, is_active=True)

        response = self.client.get(self.url(self.user1.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/friend_requests.html")
        self.assertIn("friend_requests", response.context)
        self.assertIn("user_sent_friend_requests", response.context)

        friend_requests = response.context["friend_requests"]
        self.assertEqual(friend_requests.count(), 1)
        self.assertEqual(friend_requests.first().sender, self.user2)

        user_sent_requests = response.context["user_sent_friend_requests"]
        self.assertEqual(user_sent_requests.count(), 1)
        self.assertEqual(user_sent_requests.first().receiver, self.user2)


class AcceptFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@example.com", password="StrongPass123!"
        )
        FriendList.objects.create(user=self.user1)
        FriendList.objects.create(user=self.user2)
        self.friend_request = FriendRequest.objects.create(
            sender=self.user2, receiver=self.user1, is_active=True
        )
        self.url = lambda fr_id: reverse("users:friend_request_accept", kwargs={"friend_request_id": fr_id})


    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url(self.friend_request.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_accept_friend_request_success(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.post(self.url(self.friend_request.id), secure=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("friend request accepted", data.get("message", "").lower())
        self.assertFalse(FriendRequest.objects.filter(id=self.friend_request.id).exists())

    def test_accept_other_users_request(self):
        self.client.login(username="user2", password="StrongPass123!")
        response = self.client.post(self.url(self.friend_request.id), secure=True)
        data = json.loads(response.content)
        self.assertIn("not your request", data.get("message", "").lower())

    def test_accept_nonexistent_request(self):
        self.client.login(username="user1", password="StrongPass123!")
        invalid_id = self.friend_request.id + 999
        response = self.client.post(self.url(invalid_id), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_accept_missing_request_id(self):
        self.client.login(username="user1", password="StrongPass123!")
        url = reverse("users:friend_request_accept", kwargs={"friend_request_id": 0})
        response = self.client.post(url, secure=True)
        self.assertEqual(response.status_code, 404)


class DeclineFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
        username="user1", email="u1@example.com", password="StrongPass123!"
        )
        self.user2 = User.objects.create_user(
        username="user2", email="u2@example.com", password="StrongPass123!"
        )
        self.friend_request = FriendRequest.objects.create(
        sender=self.user2, receiver=self.user1, is_active=True
        )
        self.url = lambda fr_id: reverse(
        "users:friend_request_decline", kwargs={"friend_request_id": fr_id}
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url(self.friend_request.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_decline_success(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.get(self.url(self.friend_request.id), secure=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("friend request declined", data.get("message", "").lower())

        fr = FriendRequest.objects.get(pk=self.friend_request.id)
        self.assertFalse(fr.is_active)

    def test_decline_wrong_user(self):
        self.client.login(username="user2", password="StrongPass123!")
        response = self.client.get(self.url(self.friend_request.id), secure=True)
        data = json.loads(response.content)
        self.assertIn("not your friend request", data.get("message", "").lower())

    def test_decline_invalid_request_id(self):
        self.client.login(username="user1", password="StrongPass123!")
        invalid_id = self.friend_request.id + 999
        response = self.client.get(reverse("users:friend_request_decline", kwargs={"friend_request_id": invalid_id}), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        self.client.login(username="user1", password="StrongPass123!")
        response = self.client.post(self.url(self.friend_request.id), secure=True)
        data = json.loads(response.content)
        self.assertIn("must be authenticated", data.get("message", "").lower())


class FollowUserViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@example.com", password="pass1234"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@example.com", password="pass1234"
        )
        self.url = lambda user_id: reverse("users:follow_user", args=[user_id])

    def test_follow_user_success(self):
        self.client.login(username="user1", password="pass1234")
        response = self.client.post(self.url(self.user2.id), secure=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("now following", data["message"].lower())
        self.assertEqual(Follow.objects.count(), 1)

        follow_instance = Follow.objects.first()
        self.assertEqual(follow_instance.follower, self.user1)
        self.assertEqual(follow_instance.followed, self.user2)

    def test_follow_user_already_following(self):
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.login(username="user1", password="pass1234")
        response = self.client.post(self.url(self.user2.id), secure=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("already following", data["message"].lower())
        self.assertEqual(Follow.objects.count(), 1)  # still only one follow

    def test_follow_user_invalid_method(self):
        self.client.login(username="user1", password="pass1234")
        response = self.client.get(self.url(self.user2.id), secure=True)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("invalid request", data["error"].lower())

    def test_follow_non_existent_user(self):
        self.client.login(username="user1", password="pass1234")
        non_existent_id = self.user2.id + 999
        response = self.client.post(self.url(non_existent_id), secure=True)
        self.assertEqual(response.status_code, 404)


class UnfollowUserViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.client.login(username="user1", password="pass123")

        self.url = lambda user_id: reverse("users:unfollow_user", args=[user_id])

    def test_unfollow_success(self):
        Follow.objects.create(follower=self.user1, followed=self.user2)
        response = self.client.post(self.url(self.user2.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            _("You have unfollowed %s.") % self.user2.userprofile.profile_name
        )
        self.assertFalse(
            Follow.objects.filter(follower=self.user1, followed=self.user2).exists()
        )

    def test_unfollow_not_following(self):
        response = self.client.post(self.url(self.user2.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            _("You are not following %s.") % self.user2.userprofile.profile_name
        )

    def test_unfollow_invalid_user(self):
        invalid_id = 9999
        response = self.client.post(self.url(invalid_id), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_unfollow_wrong_method(self):
        response = self.client.get(self.url(self.user2.id), secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid request", response.json()["error"])


class FollowersListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.follower = User.objects.create_user(username="follower", password="pass")
        self.follower_profile_name = self.follower.userprofile.profile_name
        Follow.objects.create(follower=self.follower, followed=self.user)
        self.url = lambda user_id: reverse("users:followers_list", args=[user_id])

    def test_followers_list_authenticated(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(self.url(self.user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/followers_list.html")
        self.assertContains(response, self.follower_profile_name)

    def test_followers_list_unauthenticated(self):
        response = self.client.get(self.url(self.user.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_followers_passed_in_context(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(self.url(self.user.id), secure=True)
        followers_context = response.context["followers"]
        self.assertEqual(len(followers_context), 1)
        self.assertEqual(followers_context[0]["user"], self.follower)
        self.assertEqual(followers_context[0]["profile_name"], self.follower_profile_name)
        self.assertEqual(response.context["profile_user"], self.user)
        self.assertEqual(response.context["page_title"], "Followers :: PlayStyle Compass")


class FollowingListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.following_user = User.objects.create_user(username="following", password="pass")
        self.following_profile_name = self.following_user.userprofile.profile_name
        Follow.objects.create(follower=self.user, followed=self.following_user)
        self.url = lambda user_id: reverse("users:following_list", args=[user_id])

    def test_following_list_authenticated(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(self.url(self.user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/following_list.html")
        self.assertContains(response, self.following_profile_name)

    def test_following_list_unauthenticated(self):
        response = self.client.get(self.url(self.user.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_following_passed_in_context(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(self.url(self.user.id), secure=True)
        following_context = response.context["following"]
        self.assertEqual(len(following_context), 1)
        self.assertEqual(following_context[0]["user"], self.following_user)
        self.assertEqual(following_context[0]["profile_name"], self.following_profile_name)
        self.assertEqual(response.context["profile_user"], self.user)
        self.assertEqual(response.context["page_title"], "Following :: PlayStyle Compass")


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_friends"])
    sys.exit(bool(failures))