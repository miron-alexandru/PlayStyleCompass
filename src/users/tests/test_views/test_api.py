from .base import *
from rest_framework_api_key.models import APIKey


class ManageApiKeyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.profile = self.user.userprofile
        self.url = reverse("users:manage_api_key")

    def test_view_authenticated_with_api_key(self):
        self.profile.api_key = "test-api-key"
        self.profile.save()
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/manage_api_key.html")
        self.assertEqual(response.context["api_key"], "test-api-key")
        self.assertIn("Manage API Key", response.context["page_title"])

    def test_view_authenticated_without_api_key(self):
        self.profile.api_key = ""
        self.profile.save()
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["api_key"])

    def test_post_request_not_allowed(self):
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Modifications are not allowed")

    def test_requires_login(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class GenerateApiKeyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.profile = self.user.userprofile
        self.url = reverse("users:generate_api_key")

    def test_generate_new_api_key_if_missing(self):
        self.profile.api_key = ""
        self.profile.save()
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(len(self.profile.api_key) > 0)
        self.assertEqual(response.json()["api_key"], self.profile.api_key)
        self.assertTrue(APIKey.objects.filter(name=self.user.username).exists())

    def test_does_not_regenerate_existing_api_key(self):
        self.profile.api_key = "existing-key"
        self.profile.save()
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["api_key"], "existing-key")
        self.assertFalse(APIKey.objects.filter(name=self.user.username).exists())

    def test_requires_login(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class RevokeApiKeyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.profile = self.user.userprofile
        self.url = reverse("users:revoke_api_key")

    def test_revoke_existing_api_key(self):
        api_key_obj, key = APIKey.objects.create_key(name=self.user.username)
        self.profile.api_key = key
        self.profile.save()

        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

        api_key_obj.refresh_from_db()
        self.assertTrue(api_key_obj.revoked)

        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.api_key)

    def test_no_active_api_key(self):
        self.client.login(username="user1", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "No active API key found")

    def test_invalid_request_method(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid request")

    def test_requires_login(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_api"])
    sys.exit(bool(failures))