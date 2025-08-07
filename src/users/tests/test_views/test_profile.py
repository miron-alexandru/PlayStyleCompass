from .base import *
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile



class ProfileUpdateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="StrongPass123!"
        )
        self.profile = self.user.userprofile
        self.url = reverse("users:change_profile_name")

    def test_get_view_shows_form(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/profile_name_update.html")
        self.assertContains(response, self.profile.profile_name)

    def test_post_valid_updates_name_and_time(self):
        self.client.login(username="testuser", password="StrongPass123!")
        new_name = "UpdatedName"
        response = self.client.post(self.url, {"profile_name": new_name}, secure=True)

        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.profile_name, new_name)
        self.assertIsNotNone(self.profile.name_last_update_time)

    def test_post_too_soon_shows_error_and_redirects(self):
        self.profile.name_last_update_time = timezone.now()
        self.profile.save()

        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(self.url, {"profile_name": "AnotherName"}, secure=True)

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("once per hour" in str(m) for m in messages))

    def test_updates_reviews_on_name_change(self):
        game = Game.objects.create(guid="12384", title="Test Game")

        Review.objects.create(
            game=game,
            user=self.user,
            reviewers="OldName",
            review_deck="Deck A",
            review_description="Solid gameplay",
            score=4
        )
        self.client.login(username="testuser", password="StrongPass123!")

        new_name = "NewName"
        self.client.post(self.url, {"profile_name": new_name}, secure=True)

        review = Review.objects.get(user=self.user)
        self.assertEqual(review.reviewers, new_name)

    def test_success_message_shown(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(self.url, {"profile_name": "SomeName"}, secure=True, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully changed" in str(m) for m in messages))


class UpdateProfilePictureTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPass123!",
            email="test@example.com",
        )
        self.url = reverse("users:profile_picture")

    def get_temp_image(self):
        image = Image.new("RGB", (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file, format="JPEG")
        tmp_file.seek(0)
        return SimpleUploadedFile("test.jpg", tmp_file.read(), content_type="image/jpeg")

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_loads_for_logged_user(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/update_profile_picture.html")

    def test_post_valid_image_updates_picture(self):
        self.client.login(username="testuser", password="StrongPass123!")
        image = self.get_temp_image()
        response = self.client.post(self.url, {"profile_picture": image}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.userprofile.profile_picture.name)

    def test_post_invalid_data_shows_form_errors(self):
        self.client.login(username="testuser", password="StrongPass123!")
        fake_image = SimpleUploadedFile(
            "fake.jpg", b"notarealimage", content_type="image/jpeg"
        )
        response = self.client.post(self.url, {"profile_picture": fake_image}, secure=True)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)


class ProfileDetailsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="StrongPass123!"
        )
        self.profile = self.user.userprofile
        self.url = reverse("users:profile_details")

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_loads_form(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/profile_details.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["user_profile"], self.profile)

    def test_post_valid_data_updates_profile(self):
        self.client.login(username="testuser", password="StrongPass123!")
        valid_data = {
            "bio": "New bio",
            "favorite_game": "Game",
            "gaming_genres": ["RPG", "MMO"],
            "favorite_game_modes": ["Story Mode"],
            "social_media": "https://facebook.com/testuser",
            "gaming_alias": "alias123",
            "current_game": "GameX",
            "last_finished_game": "GameY",
            "favorite_franchise": "Franchise1",
            "favorite_character": "Character1",
            "favorite_soundtrack": "Soundtrack1",
            "gaming_commitment": "hardcore",
            "main_gaming_platform": "pc",
            "gaming_setup": "Dual monitors",
            "streaming_preferences": "Twitch",
        }

        response = self.client.post(self.url, valid_data, secure=True)
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "New bio")
        self.assertIn("RPG, MMO", self.profile.gaming_genres)
        self.assertIn("Story Mode", self.profile.favorite_game_modes)

    def test_post_invalid_data_shows_error(self):
        self.client.login(username="testuser", password="StrongPass123!")
        invalid_data = {
            "bio": "New bio",
            "gaming_genres": ["RPG", "MMO"],
            "favorite_game_modes": ["Story Mode"],
            "social_media": "invalid-url",
        }
        response = self.client.post(self.url, invalid_data, secure=True)
        self.assertEqual(response.status_code, 200)

        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertIn("social_media", form.errors)
        self.assertIn("Please enter a valid social media link.", form.errors["social_media"])

        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.bio, "New bio")

    def test_post_with_reset_profile_clears_fields(self):
        self.client.login(username="testuser", password="StrongPass123!")
        self.profile.bio = "Something"
        self.profile.gaming_alias = "Alias"
        self.profile.save()

        response = self.client.post(self.url, {"reset_profile": "1"}, secure=True)
        self.assertEqual(response.status_code, 302)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "")
        self.assertEqual(self.profile.gaming_alias, "")


class ViewProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="StrongPass123!"
        )
        self.profile = self.user.userprofile
        self.profile.profile_name = "testprofile"
        self.profile.save()
        self.url = reverse("users:view_profile", kwargs={"profile_name": self.profile.profile_name})

        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="StrongPass456!"
        )
        self.other_profile = self.other_user.userprofile
        self.other_profile.profile_name = "otherprofile"
        self.other_profile.save()

    def test_view_profile_exists(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/user_profile.html")
        self.assertIn("user_profile", response.context)
        self.assertEqual(response.context["user_profile"].profile_name, "testprofile")

    def test_view_profile_not_found(self):
        url = reverse("users:view_profile", kwargs={"profile_name": "nonexistent"})
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"exists": False})

    def test_view_profile_authenticated_flags(self):
        self.client.login(username="testuser", password="StrongPass123!")

        self.user.userprofile.blocked_users.add(self.other_user)
        self.user.userprofile.save()

        Follow.objects.create(follower=self.user, followed=self.other_user)

        url = reverse("users:view_profile", kwargs={"profile_name": self.other_profile.profile_name})
        response = self.client.get(url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("is_blocked", response.context)
        self.assertIn("is_following", response.context)
        self.assertIn("is_friend", response.context)
        self.assertTrue(response.context["is_blocked"])
        self.assertEqual(response.context["is_friend"], "Stranger")
        self.assertTrue(response.context["is_following"])

    def test_view_profile_anonymous_user(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["is_blocked"])
        self.assertIsNone(response.context["is_following"])


class ToggleShowStatTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="StrongPass123!"
        )
        self.url = reverse("users:toggle_show_stat")

    def test_redirects_if_not_logged(self):
        response = self.client.post(
            self.url, {"statName": "reviews", "userId": self.user.id}, secure=True
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_toggles_stat(self):
        self.client.login(username="testuser", password="StrongPass123!")
        user_prefs = self.user.userpreferences
        before = getattr(user_prefs, "show_reviews", False)

        response = self.client.post(
            self.url, {"statName": "reviews", "userId": self.user.id}, secure=True
        )
        self.assertEqual(response.status_code, 200)

        user_prefs.refresh_from_db()
        after = getattr(user_prefs, "show_reviews")
        self.assertEqual(after, not before)

        json_response = response.json()
        self.assertEqual(json_response["show"], after)

    def test_invalid_stat_still_returns_true(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(
            self.url, {"statName": "nonexistent", "userId": self.user.id}, secure=True
        )
        self.assertEqual(response.status_code, 200)

        user_prefs = self.user.userpreferences
        user_prefs.refresh_from_db()

        self.assertFalse(hasattr(user_prefs, "show_nonexistent"))

        json_response = response.json()
        self.assertTrue(json_response["show"])


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_profile"])
    sys.exit(bool(failures))