from .base import *


class BlockUserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.user_profile = self.user.userprofile

        self.other_user = User.objects.create_user(username="user2", password="pass")
        self.other_profile = self.other_user.userprofile

        self.url = lambda user_id: reverse("users:block_user", args=[user_id])

    def test_block_user_success(self):
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("User has been blocked", response.json()["message"])
        self.assertIn(self.other_user, self.user_profile.blocked_users.all())

    def test_block_self(self):
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url(self.user.id), secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot block yourself", response.json()["error"].lower())
        self.assertNotIn(self.user, self.user_profile.blocked_users.all())

    def test_block_already_blocked_user(self):
        self.user_profile.blocked_users.add(self.other_user)
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("already blocked", response.json()["message"].lower())
        self.assertIn(self.other_user, self.user_profile.blocked_users.all())

    def test_invalid_request_method(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn("invalid request method", response.json()["error"].lower())

    def test_requires_login(self):
        response = self.client.post(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class UnblockUserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.user_profile = self.user.userprofile

        self.other_user = User.objects.create_user(username="user2", password="pass")
        self.other_profile = self.other_user.userprofile

        self.url = lambda user_id: reverse("users:unblock_user", args=[user_id])

    def test_unblock_user_success(self):
        self.user_profile.blocked_users.add(self.other_user)
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("user has been unblocked", response.json()["message"].lower())
        self.assertNotIn(self.other_user, self.user_profile.blocked_users.all())

    def test_unblock_self(self):
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url(self.user.id), secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot unblock yourself", response.json()["error"].lower())

    def test_unblock_user_not_blocked(self):
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("user was not blocked", response.json()["message"].lower())

    def test_invalid_request_method(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn("invalid request method", response.json()["error"].lower())

    def test_requires_login(self):
        response = self.client.post(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class CheckBlockStatusViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.user_profile = self.user.userprofile

        self.other_user = User.objects.create_user(username="user2", password="pass")
        self.other_profile = self.other_user.userprofile

        self.url = lambda user_id: reverse("users:check_block_status", args=[user_id])

    def test_user_is_blocked(self):
        self.user_profile.blocked_users.add(self.other_user)
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_blocked"])

    def test_user_is_not_blocked(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_blocked"])

    def test_requires_login(self):
        response = self.client.get(self.url(self.other_user.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class BlockListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.user_profile = self.user.userprofile

        self.other_user = User.objects.create_user(username="user2", password="pass")
        self.user_profile.blocked_users.add(self.other_user)

        self.url = reverse("users:block_list")

    def test_block_list_authenticated(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/block_list.html")
        self.assertIn(self.other_user, response.context["blocked_users"])
        self.assertIn("Block List", response.context["page_title"])

    def test_block_list_empty(self):
        self.user_profile.blocked_users.clear()
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["blocked_users"], [])

    def test_requires_login(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)
