from ..base import *


class GetRecommendationsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.preferences = self.user.userpreferences
        self.url = reverse('playstyle_compass:get_recommendations')

    @patch('playstyle_compass.views.paginate_matching_games')
    @patch('playstyle_compass.views.RecommendationEngine')
    def test_authenticated_user_gets_recommendations(self, mock_engine_class, mock_paginate):
        self.client.login(username='testuser', password='testpass')
        self.preferences.gaming_history = "Baldur's Gate III"
        self.preferences.favorite_genres = "Action, RPG"
        self.preferences.save()

        mock_engine_instance = mock_engine_class.return_value
        mock_engine_instance.matching_games = ['Game1', 'Game2']
        mock_engine_instance.process.return_value = None
        mock_paginate.return_value = {"page_obj": ['Game1', 'Game2']}

        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/recommendations.html")
        self.assertIn("paginated_games", response.context)
        self.assertEqual(response.context["user_preferences"], self.preferences)

    def test_redirects_if_missing_preferences(self):
        self.client.login(username='testuser', password='testpass')
        self.preferences.gaming_history = ""
        self.preferences.favorite_genres = ""
        self.preferences.save()

        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('playstyle_compass:update_preferences'))

    def test_unauthenticated_user_redirected(self):
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class SearchResultsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:search_results')

        self.game = Game.objects.create(title="The Witcher III", guid="12345")

    def test_valid_search_query_real_render(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "Witcher"}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/search_games.html")
        self.assertContains(response, "The Witcher III")

    def test_search_with_no_results(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "UnknownTitle"}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/search_games.html")
        self.assertContains(response, "UnknownTitle")
        self.assertEqual(len(response.context["games"].object_list), 0)

    def test_query_too_short_returns_400(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "A"}, secure=True)

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid query", status_code=400)

    def test_empty_query_renders_page(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": ""}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/search_games.html")
        self.assertEqual(response.context["query"], "")

class AutocompleteGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:autocomplete')
        Game.objects.create(title="Hollow Knight", guid="001")
        Game.objects.create(title="Hogwarts Legacy", guid="002")

    def test_autocomplete_returns_matching_games(self):
        response = self.client.get(self.url, {"query": "Ho"}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        titles = [item["title"] for item in data["results"]]

        self.assertIn("Hollow Knight", titles)
        self.assertIn("Hogwarts Legacy", titles)

    def test_autocomplete_returns_no_matches(self):
        response = self.client.get(self.url, {"query": "Zelda"}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["results"], [])

    def test_autocomplete_empty_query_returns_empty_list(self):
        response = self.client.get(self.url, {"query": ""}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["results"], [])


class SimilarPlaystylesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.different_user = User.objects.create_user(username="diffuser", password="testpass")

        self.user.userpreferences.gaming_history = "Long"
        self.user.userpreferences.favorite_genres = "Action, Adventure"
        self.user.userpreferences.themes = "Fantasy"
        self.user.userpreferences.platforms = "PC"
        self.user.userpreferences.save()

        self.other_user.userpreferences.gaming_history = "Long"
        self.other_user.userpreferences.favorite_genres = "Action, Adventure"
        self.other_user.userpreferences.themes = "Fantasy"
        self.other_user.userpreferences.platforms = "PC"
        self.other_user.userpreferences.save()

        self.different_user.userpreferences.gaming_history = "Short"
        self.different_user.userpreferences.favorite_genres = "Puzzle"
        self.different_user.userpreferences.themes = "Sci-fi"
        self.different_user.userpreferences.platforms = "Mobile"
        self.different_user.userpreferences.save()

        self.client.login(username="testuser", password="testpass")
        self.url = reverse("playstyle_compass:similar_playstyles")

    def test_view_loads(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "misc/similar_playstyles.html")

    def test_shows_similar_users(self):
        response = self.client.get(self.url, secure=True)
        users = response.context["similar_user_playstyles"]
        self.assertIn(self.other_user.userpreferences, users)

    def test_hides_different_users(self):
        response = self.client.get(self.url, secure=True)
        users = response.context["similar_user_playstyles"]
        self.assertNotIn(self.different_user.userpreferences, users)

    def test_gives_user_preferences(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.context["user_preferences"], self.user.userpreferences)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_recommendations"])
    sys.exit(bool(failures))
