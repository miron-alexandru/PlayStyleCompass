from django.utils.translation import gettext_lazy as _
from ..base import *


class GamingPreferencesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_view_renders_for_authenticated_user(self):
        """Authenticated user gets 200 OK and correct context"""
        self.client.login(username="testuser", password="password123")
        response = self.client.get(
            reverse("playstyle_compass:gaming_preferences"), secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "preferences/create_gaming_preferences.html")
        self.assertEqual(
            response.context["page_title"], _("Define PlayStyle :: PlayStyle Compass")
        )
        self.assertEqual(response.context["genres"], genres)
        self.assertEqual(response.context["platforms"], all_platforms)
        self.assertEqual(response.context["themes"], all_themes)
        self.assertEqual(response.context["game_styles"], game_style)
        self.assertEqual(response.context["connection_types"], connection_type)

    def test_redirect_if_not_logged_in(self):
        """Unauthenticated users should be redirected to login page"""
        response = self.client.get(
            reverse("playstyle_compass:gaming_preferences"), secure=True
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

class UserPreferencesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.preferences = self.user.userpreferences
        self.update_preferences_url = reverse('playstyle_compass:update_preferences')

    def test_update_preferences_get(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.update_preferences_url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'preferences/update_gaming_preferences.html')
        self.assertIn('user_preferences', response.context)
        self.assertEqual(response.context['user_preferences'], self.preferences)

    def test_update_preferences_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'gaming_history': 'Intermediate',
            'favorite_genres': ['RPG', 'Strategy'],
            'themes': ['Dark', 'Sci-fi'],
            'platforms': ['PC', 'Console'],
            'connection_types': ['Solo', 'Co-op'],
            'game_styles': ['Casual', 'Competitive'],
        }
        response = self.client.post(self.update_preferences_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.preferences.gaming_history, 'Intermediate')
        self.assertEqual(self.preferences.favorite_genres, 'RPG, Strategy')
        self.assertEqual(self.preferences.themes, 'Dark, Sci-fi')
        self.assertEqual(self.preferences.platforms, 'PC, Console')
        self.assertEqual(self.preferences.connection_types, 'Solo, Co-op')
        self.assertEqual(self.preferences.game_styles, 'Casual, Competitive')

    def test_update_preferences_unauthenticated_redirect(self):
        response = self.client.get(self.update_preferences_url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

        response_post = self.client.post(self.update_preferences_url, {}, secure=True)
        self.assertEqual(response_post.status_code, 302)
        self.assertIn('/users/login/', response_post.url)


class ClearPreferencesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.preferences = self.user.userpreferences
        self.url = reverse('playstyle_compass:clear_preferences')

        self.preferences.gaming_history = "Some history"
        self.preferences.favorite_genres = "Genre1, Genre2"
        self.preferences.themes = "Theme1, Theme2"
        self.preferences.platforms = "Platform1, Platform2"
        self.preferences.connection_types = "Connection1, Connection2"
        self.preferences.game_styles = "Style1, Style2"
        self.preferences.save()

    def test_clear_preferences_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, secure=True)

        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('playstyle_compass:update_preferences'))

        self.assertEqual(self.preferences.gaming_history, "")
        self.assertEqual(self.preferences.favorite_genres, "")
        self.assertEqual(self.preferences.themes, "")
        self.assertEqual(self.preferences.platforms, "")
        self.assertEqual(self.preferences.connection_types, "")
        self.assertEqual(self.preferences.game_styles, "")

    def test_unauthenticated_user_redirected(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)


class SaveUserPreferencesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.preferences = self.user.userpreferences

        self.connection_types_url = reverse('playstyle_compass:save_connection_types')
        self.game_styles_url = reverse('playstyle_compass:save_game_styles')
        self.gaming_history_url = reverse('playstyle_compass:save_gaming_history')
        self.favorite_genres_url = reverse('playstyle_compass:save_favorite_genres')
        self.themes_url = reverse('playstyle_compass:save_themes')
        self.platforms_url = reverse('playstyle_compass:save_platforms')
        self.redirect_url = reverse('playstyle_compass:update_preferences')

    def test_save_connection_types_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {'connection_types': ['Solo', 'Co-op']}
        response = self.client.post(self.connection_types_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.preferences.connection_types, 'Solo, Co-op')

    def test_save_game_styles_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {'game_styles': ['Casual', 'Competitive']}
        response = self.client.post(self.game_styles_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.preferences.game_styles, 'Casual, Competitive')

    def test_save_gaming_history_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {'gaming_history': ['Newbie', 'Veteran']}
        response = self.client.post(self.gaming_history_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.preferences.gaming_history, 'Newbie, Veteran')

    def test_save_favorite_genres_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {'favorite_genres': ['RPG', 'FPS']}
        response = self.client.post(self.favorite_genres_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.preferences.favorite_genres, 'RPG, FPS')

    def test_save_themes_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {'themes': ['Dark', 'Fantasy']}
        response = self.client.post(self.themes_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.preferences.themes, 'Dark, Fantasy')

    def test_save_platforms_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {'platforms': ['PC', 'Console']}
        response = self.client.post(self.platforms_url, data, secure=True)
        self.preferences.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.preferences.platforms, 'PC, Console')

    def test_unauthenticated_user_redirected(self):
        response = self.client.post(self.connection_types_url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)


class SaveAllPreferencesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.preferences = self.user.userpreferences
        self.url = reverse('playstyle_compass:save_all_preferences')

    def test_save_all_preferences_post(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'gaming_history': ['History1', 'History2'],
            'favorite_genres': ['Genre1', 'Genre2'],
            'themes': ['Theme1', 'Theme2'],
            'platforms': ['Platform1', 'Platform2'],
            'connection_types': ['Connection1', 'Connection2'],
            'game_styles': ['Style1', 'Style2'],
        }
        response = self.client.post(self.url, data, secure=True)
        self.preferences.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        self.assertEqual(self.preferences.gaming_history, 'History1, History2')
        self.assertEqual(self.preferences.favorite_genres, 'Genre1, Genre2')
        self.assertEqual(self.preferences.themes, 'Theme1, Theme2')
        self.assertEqual(self.preferences.platforms, 'Platform1, Platform2')
        self.assertEqual(self.preferences.connection_types, 'Connection1, Connection2')
        self.assertEqual(self.preferences.game_styles, 'Style1, Style2')

    def test_save_all_preferences_get_does_nothing(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, secure=True)
        self.preferences.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        self.assertEqual(self.preferences.gaming_history, '')
        self.assertEqual(self.preferences.favorite_genres, '')
        self.assertEqual(self.preferences.themes, '')
        self.assertEqual(self.preferences.platforms, '')
        self.assertEqual(self.preferences.connection_types, '')
        self.assertEqual(self.preferences.game_styles, '')

    def test_unauthenticated_user_redirected(self):
        response = self.client.post(self.url, {}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_preferences"])
    sys.exit(bool(failures))
