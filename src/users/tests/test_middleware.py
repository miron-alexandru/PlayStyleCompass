import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone, translation
from django.core.exceptions import ObjectDoesNotExist

from users.middleware import UserTimezoneMiddleware, UserLanguageMiddleware
from users.models import UserProfile


class UserTimezoneMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = UserTimezoneMiddleware(lambda r: "response")
        self.user = User.objects.create_user(username="test", password="pass")
        self.profile = self.user.userprofile
        self.profile.timezone = "UTC"
        self.profile.save()

    def test_updates_timezone_if_different(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {"detected_tz": "Europe/Berlin"}
        timezone.activate("Europe/Berlin")

        response = self.middleware(request)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.timezone, "Europe/Berlin")
        self.assertEqual(response, "response")

    def test_does_not_update_if_same_timezone(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {"detected_tz": "UTC"}
        timezone.activate("UTC")

        response = self.middleware(request)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.timezone, "UTC")
        self.assertEqual(response, "response")

    def test_no_detected_timezone_in_session(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {}
        timezone.activate("UTC")

        response = self.middleware(request)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.timezone, "UTC")
        self.assertEqual(response, "response")

    def test_unauthenticated_user(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        request.session = {"detected_tz": "Europe/Berlin"}
        timezone.activate("Europe/Berlin")

        response = self.middleware(request)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.timezone, "UTC")
        self.assertEqual(response, "response")

    def test_user_without_profile(self):
        user = User.objects.create_user(username="noprof", password="pass")
        user.userprofile.delete()

        request = self.factory.get("/")
        request.user = user
        request.session = {"detected_tz": "Europe/Berlin"}
        timezone.activate("Europe/Berlin")

        response = self.middleware(request)
        self.assertEqual(response, "response")


class UserLanguageMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = UserLanguageMiddleware(lambda r: "response")
        self.user = User.objects.create_user(username="test", password="pass")
        self.profile = self.user.userprofile
        self.profile.language = "fr"
        self.profile.save()

    def test_sets_language_from_profile(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {}

        response = self.middleware(request)
        self.assertEqual(request.session["django_language"], "fr")
        self.assertEqual(translation.get_language(), "fr")
        self.assertEqual(response, "response")

    def test_default_language_if_missing(self):
        self.profile.language = ""
        self.profile.save()

        request = self.factory.get("/")
        request.user = self.user
        request.session = {}

        response = self.middleware(request)
        self.assertEqual(request.session["django_language"], "en")
        self.assertEqual(translation.get_language(), "en")
        self.assertEqual(response, "response")

    def test_unauthenticated_user(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        request.session = {}

        response = self.middleware(request)

        self.assertNotIn("django_language", request.session)
        self.assertEqual(response, "response")

    def test_user_without_profile(self):
        user = User.objects.create_user(username="noprof", password="pass")
        user.userprofile.delete()

        request = self.factory.get("/")
        request.user = user
        request.session = {}

        response = self.middleware(request)

        self.assertEqual(response, "response")


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_middleware"])
    sys.exit(bool(failures))