import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()


import random
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from playstyle_compass.models import *
from playstyle_compass.forms import *
from users.models import *
from playstyle_compass.views import (
    genres,
    all_platforms,
    all_themes,
    game_style,
    connection_type,
)


class IndexViewTest(TestCase):
    def setUp(self):
        """Set up test data for all tests"""
        used_guids = set()

        def unique_guid():
            while True:
                guid = str(random.randint(10000, 99999))
                if guid not in used_guids:
                    used_guids.add(guid)
                    return guid

        upcoming_titles = [
            "Little Nightmares III",
            "Assassin's Creed Shadows",
            "Astrobotanica",
            "Death Stranding 2: On the Beach",
            "Earthblade",
            "Vampire: The Masquerade - Bloodlines 2",
            "Subnautica 2",
            "Grand Theft Auto VI",
            "Wuchang: Fallen Feathers",
            "The Relic: First Guardian",
        ]
        popular_titles = [
            "Honkai: Star Rail",
            "Diablo IV",
            "Fortnite",
            "Overwatch",
            "The Witcher 3: Wild Hunt",
            "Baldur's Gate 3",
            "League of Legends",
            "Hogwarts Legacy",
            "NieR:Automata",
            "Palworld",
        ]
        franchise_titles = [
            "Assassin's Creed",
            "Tomb Raider",
            "Grand Theft Auto",
            "Mortal Kombat",
            "Halo",
            "Battlefiled",
            "God of War",
            "The Witcher",
            "The Sims",
            "FIFA",
        ]

        for title in upcoming_titles + popular_titles:
            Game.objects.create(title=title, average_score=8.0, guid=unique_guid())

        for title in franchise_titles:
            Franchise.objects.create(title=title)

        for i in range(6):
            News.objects.create(
                article_id=f"article-{i}",
                title=f"News {i}",
                summary="Some summary",
                url=f"https://example.com/news/{i}",
                image=f"https://example.com/image{i}.jpg",
                publish_date=f"2025-07-0{i+1}",
                platforms="PC, PS5",
            )

        for i in range(10):
            Game.objects.create(
                title=f"Top Rated Game {i}", average_score=10 - i, guid=unique_guid()
            )

        for i in range(8):
            Deal.objects.create(
                deal_id=f"deal-{i}",
                game_name=f"Game {i}",
                sale_price=19.99,
                retail_price=39.99,
                thumb_url=f"https://example.com/thumb{i}.jpg",
                store_name="Steam",
                store_icon_url="https://example.com/steam-icon.png",
            )

    def test_index_view_returns_200(self):
        """The index view returns a 200 status code"""
        response = self.client.get(reverse("playstyle_compass:index"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        """The index view uses the correct HTML template"""
        response = self.client.get(reverse("playstyle_compass:index"), follow=True)
        self.assertTemplateUsed(response, "base/index.html")

    def test_index_view_context_data(self):
        """The index view passes the expected context variables"""
        response = self.client.get(reverse("playstyle_compass:index"), follow=True)
        context = response.context

        self.assertEqual(context["page_title"], _("Home :: PlayStyle Compass"))
        self.assertEqual(context["search_bar_type"], "search_games")

        self.assertIn("upcoming_games", context)
        self.assertEqual(context["upcoming_games"].count(), 10)

        self.assertIn("popular_games", context)
        self.assertEqual(context["popular_games"].count(), 10)

        self.assertIn("popular_franchises", context)
        self.assertEqual(context["popular_franchises"].count(), 10)

        self.assertIn("articles", context)
        self.assertEqual(context["articles"].count(), 6)

        self.assertIn("top_rated_games", context)
        self.assertEqual(context["top_rated_games"].count(), 10)

        self.assertIn("game_deals", context)
        self.assertEqual(context["game_deals"].count(), 8)


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


class SearchFranchisesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:search_franchises')  # Update if your URL name differs

        self.franchise = Franchise.objects.create(title="The Legend of Zelda")

    def test_valid_search_query_real_render(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "Zelda"}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/search_franchises.html")
        self.assertContains(response, "The Legend of Zelda")

    def test_search_with_no_results(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "UnknownFranchise"}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/search_franchises.html")
        self.assertContains(response, "UnknownFranchise")
        self.assertEqual(len(response.context["franchises"].object_list), 0)

    def test_query_too_short_returns_400(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": "A"}, secure=True)

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid query", status_code=400)

    def test_empty_query_renders_page(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {"query": ""}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/search_franchises.html")
        self.assertEqual(response.context["query"], "")


class AutocompleteGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:autocomplete')  # Update if needed
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


class AutocompleteFranchisesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('playstyle_compass:autocomplete_franchises')
        Franchise.objects.create(title="The Legend of Zelda")
        Franchise.objects.create(title="The Witcher")

    def test_autocomplete_returns_matching_franchises(self):
        response = self.client.get(self.url, {"query": "The"}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        titles = [item["title"] for item in data["results"]]

        self.assertIn("The Legend of Zelda", titles)
        self.assertIn("The Witcher", titles)

    def test_autocomplete_returns_no_matches(self):
        response = self.client.get(self.url, {"query": "Mario"}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["results"], [])

    def test_autocomplete_empty_query_returns_empty_list(self):
        response = self.client.get(self.url, {"query": ""}, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["results"], [])


class ToggleFavoriteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.game = Game.objects.create(title='Stardew Valley', guid='343')
        self.preferences = self.user.userpreferences
        self.url = reverse('playstyle_compass:toggle_favorite')

    def test_add_game_to_favorites(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'game_id': self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"is_favorite": True})
        self.assertIn(self.game, self.preferences.favorite_games.all())

    def test_remove_game_from_favorites(self):
        self.preferences.favorite_games.add(self.game)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'game_id': self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"is_favorite": False})
        self.assertNotIn(self.game, self.preferences.favorite_games.all())

    def test_unauthenticated_user_redirected(self):
        response = self.client.post(self.url, {'game_id': self.game.guid}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_invalid_game_returns_404(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'game_id': 'invalid-guid'}, secure=True)
        self.assertEqual(response.status_code, 404)

    def test_get_request_returns_405(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {'game_id': self.game.guid}, secure=True)
        self.assertEqual(response.status_code, 405)


class ToggleGameQueueViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.game = Game.objects.create(title="Test Game", guid="34123")
        self.url = reverse("playstyle_compass:toggle_game_queue")

    def test_toggle_adds_game_to_queue(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"in_queue": True})
        self.assertIn(self.game, self.user.userpreferences.game_queue.all())

    def test_toggle_removes_game_from_queue(self):
        self.client.login(username="testuser", password="testpass")
        self.user.userpreferences.game_queue.add(self.game)

        response = self.client.post(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"in_queue": False})
        self.assertNotIn(self.game, self.user.userpreferences.game_queue.all())

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.post(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_request_returns_405(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 405)


class ToggleGameQueueViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.game = Game.objects.create(title="Test Game", guid="54123")
        self.url = reverse("playstyle_compass:toggle_game_queue")

    def test_toggle_adds_game_to_queue(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"in_queue": True})
        self.assertIn(self.game, self.user.userpreferences.game_queue.all())

    def test_toggle_removes_game_from_queue(self):
        self.client.login(username="testuser", password="testpass")
        self.user.userpreferences.game_queue.add(self.game)

        response = self.client.post(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"in_queue": False})
        self.assertNotIn(self.game, self.user.userpreferences.game_queue.all())

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.post(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_request_returns_405(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url, {"game_id": self.game.guid}, secure=True)

        self.assertEqual(response.status_code, 405)


class UserReviewsViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="testpass")
        self.user1.userprofile.profile_name = "User One"
        self.user1.userprofile.save()
        self.user1.userpreferences.show_reviews = True
        self.user1.userpreferences.save()

        self.user2 = User.objects.create_user(username="user2", password="testpass")
        self.user2.userprofile.profile_name = "User Two"
        self.user2.userprofile.save()
        self.user2.userpreferences.show_reviews = True
        self.user2.userpreferences.save()

        self.game = Game.objects.create(title="Test Game", guid="64341")
        self.review = Review.objects.create(
            game=self.game,
            user=self.user1,
            reviewers="Reviewer A",
            review_deck="Deck A",
            review_description="A solid review.",
            score=4,
            date_added=now()
        )

        self.url = reverse("playstyle_compass:user_reviews")
        self.other_url = reverse("playstyle_compass:user_reviews_with_id", kwargs={"user_id": self.user2.id})

    def test_view_own_reviews(self):
        self.client.login(username="user1", password="testpass")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/user_reviews.html")
        self.assertIn(self.game, response.context["games"])
        self.assertFalse(response.context["other_user"])
        self.assertEqual(response.context["user_name"], "User One")

    def test_view_other_user_reviews_allowed(self):
        self.client.login(username="user1", password="testpass")
        response = self.client.get(self.other_url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/user_reviews.html")
        self.assertTrue(response.context["other_user"])
        self.assertEqual(response.context["user_name"], "User Two")

    def test_view_other_user_reviews_disallowed(self):
        self.client.login(username="user1", password="testpass")
        self.user2.userpreferences.show_reviews = False
        self.user2.userpreferences.save()

        response = self.client.get(self.other_url, follow=True)
        self.assertRedirects(
            response,
            "https://testserver" + reverse("playstyle_compass:index"),
            status_code=301,
             target_status_code=200,
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(str(_("You don't have permission to view this content.")) in str(message) for message in messages))

    def test_login_required(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class UserGamesViewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="testpass")
        self.user2 = User.objects.create_user(username="user2", password="testpass")

        self.client.login(username="user1", password="testpass")

    def test_view_own_favorite_games(self):
        response = self.client.get(reverse("playstyle_compass:favorite_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Favorites")
        self.assertFalse(response.context["other_user"])

    def test_view_other_user_favorite_games_disallowed(self):
        self.user2.userpreferences.show_favorites = False
        self.user2.userpreferences.save()

        url = reverse("playstyle_compass:favorite_games_with_id", kwargs={"user_id": self.user2.id})
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("playstyle_compass:index"))
        response_follow = self.client.get(response.url, secure=True)
        messages = list(get_messages(response_follow.wsgi_request))
        self.assertTrue(any("don't have permission" in str(message) for message in messages))

    def test_view_other_user_favorite_games_allowed(self):
        self.user2.userpreferences.show_favorites = True
        self.user2.userpreferences.save()

        url = reverse("playstyle_compass:favorite_games_with_id", kwargs={"user_id": self.user2.id})
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Favorites")
        self.assertTrue(response.context["other_user"])

    def test_view_other_user_game_queue_disallowed(self):
        self.user2.userpreferences.show_in_queue = False
        self.user2.userpreferences.save()

        url = reverse("playstyle_compass:game_queue_with_id", kwargs={"user_id": self.user2.id})
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("playstyle_compass:index"))
        response_follow = self.client.get(response.url, secure=True)
        messages = list(get_messages(response_follow.wsgi_request))
        self.assertTrue(any("don't have permission" in str(message) for message in messages))

    def test_view_other_user_game_queue_allowed(self):
        self.user2.userpreferences.show_in_queue = True
        self.user2.userpreferences.save()

        url = reverse("playstyle_compass:game_queue_with_id", kwargs={"user_id": self.user2.id})
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Game Queue")
        self.assertTrue(response.context["other_user"])


class TopRatedGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.game1 = Game.objects.create(title="Game One", guid="1234")
        self.game2 = Game.objects.create(title="Game Two", guid="2423")
        self.game3 = Game.objects.create(title="Game Three", guid="2928")

        # Create reviews for each game to set average_score properly
        Review.objects.create(
            game=self.game1,
            user=self.user,
            reviewers="Reviewer1",
            review_deck="Great game",
            review_description="Really enjoyed it",
            score=5,
        )
        Review.objects.create(
            game=self.game2,
            user=self.user,
            reviewers="Reviewer2",
            review_deck="Amazing!",
            review_description="One of the best",
            score=5,
        )
        Review.objects.create(
            game=self.game3,
            user=self.user,
            reviewers="Reviewer3",
            review_deck="Not so good",
            review_description="Could be better",
            score=3,
        )


    def test_top_rated_games_view(self):
        url = reverse("playstyle_compass:top_rated_games")
        response = self.client.get(url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/top_rated_games.html")

        games_in_context = list(response.context["games"])
        self.assertIn(self.game1, games_in_context)
        self.assertIn(self.game2, games_in_context)
        self.assertNotIn(self.game3, games_in_context)

        self.assertLessEqual(games_in_context[0].average_score, games_in_context[-1].average_score)


class UpcomingGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        future_date = date.today() + timedelta(days=10)
        current_year_str = str(date.today().year)

        self.upcoming1 = Game.objects.create(title="Upcoming 1", release_date=future_date, guid="231")
        self.upcoming2 = Game.objects.create(title="Upcoming 2", release_date=current_year_str, guid="2312")
        self.past_game = Game.objects.create(title="Past Game", release_date=date.today() - timedelta(days=5), guid="493")

    def test_upcoming_games_view(self):
        url = reverse("playstyle_compass:upcoming_games")
        response = self.client.get(url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/upcoming_games.html")

        paginated_games = response.context["upcoming_games"]

        self.assertIn(self.upcoming1, paginated_games)
        self.assertIn(self.upcoming2, paginated_games)
        self.assertNotIn(self.past_game, paginated_games)


class AddReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user_profile = self.user.userprofile
        self.user_profile.profile_name = "testprofile"
        self.user_profile.save()

        self.follower_user = User.objects.create_user(username="follower", password="testpass")
        self.follower_profile = self.follower_user.userprofile
        Follow.objects.create(follower=self.follower_user, followed=self.user)

        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept",
        )

        self.url = reverse("playstyle_compass:add_review", args=[self.game.guid])
        self.index_url = reverse("playstyle_compass:index")

    def test_can_get_form(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/add_review.html")
        self.assertIsInstance(response.context["form"], ReviewForm)
        self.assertEqual(response.context["game"], self.game)

    def test_can_add_review(self):
        data = {
            "review_deck": "Great game!",
            "review_description": "Really enjoyed it.",
            "score": 5,
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.index_url)

        review = Review.objects.get(game=self.game.guid, user=self.user)
        self.assertEqual(review.reviewers, "testprofile")
        self.assertEqual(review.review_deck, "Great game!")
        self.assertEqual(review.score, 5)

    def test_duplicate_review_blocked(self):
        Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="testprofile",
            review_deck="Great",
            review_description="desc",
            score=5,
        )

        response = self.client.post(self.url, {
            "review_deck": "Another",
            "review_description": "Another desc",
            "score": 4,
        }, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.index_url)

        self.assertEqual(Review.objects.filter(game=self.game.guid, user=self.user).count(), 1)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertIn("You have already reviewed this game!", [m.message for m in messages_list])

    def test_followers_get_notifications(self):
        response = self.client.post(self.url, {
            "review_deck": "Deck",
            "review_description": "Description",
            "score": 5,
        }, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.index_url)

        review = Review.objects.filter(game=self.game.guid, user=self.user).first()
        self.assertIsNotNone(review)

        notifications = Notification.objects.filter(notification_type="review", user=self.follower_user)
        self.assertEqual(notifications.count(), 1)
        notification = notifications.first()
        self.assertIn(self.user_profile.profile_name, notification.message)
        self.assertIn(self.game.title, notification.message)

    def test_redirects_to_next(self):
        next_url = reverse("playstyle_compass:view_game", args=[self.game.guid])
        response = self.client.post(
            f"{self.url}?next={next_url}",
            {
                "review_deck": "Deck",
                "review_description": "Description",
                "score": 5,
            },
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], next_url)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)

        expected_url = f"/en/users/login/?next={self.url}"
        self.assertEqual(response["Location"], expected_url)


class EditReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user_profile = self.user.userprofile
        self.user_profile.profile_name = "testprofile"
        self.user_profile.save()

        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept",
        )

        self.url = reverse("playstyle_compass:edit_review", args=[self.game.guid])
        self.index_url = reverse("playstyle_compass:index")

        self.review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers=self.user_profile.profile_name,
            review_deck="Original deck",
            review_description="Original description",
            score=3,
        )

    def test_can_view_edit_form(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/edit_review.html")
        self.assertIsInstance(response.context["form"], ReviewForm)
        self.assertEqual(response.context["game"], self.game)

    def test_can_update_review(self):
        data = {
            "review_deck": "Updated deck <script>",
            "review_description": "Updated description <b>bold</b>",
            "score": 4,
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.index_url)

        review = Review.objects.get(pk=self.review.pk)
        self.assertEqual(review.review_deck, escape(data["review_deck"]))
        self.assertEqual(review.review_description, escape(data["review_description"]))
        self.assertEqual(review.score, 4)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertIn("successfully updated", messages_list[0].message.lower())

    def test_redirect_if_no_review(self):
        self.review.delete()

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.index_url)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertIn("You haven't written any reviews for this game!", [m.message for m in messages_list])

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)

        login_url = f"/en/users/login/?next={self.url}"
        self.assertEqual(response["Location"], login_url)


class GameReviewsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.game = Game.objects.create(
            guid="453123",
            title="Test Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept",
        )

        self.url = reverse("playstyle_compass:get_game_reviews", args=[self.game.guid])

        Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="testprofile",
            review_deck="Good game",
            review_description="Really liked it",
            score=4,
            likes=10,
            dislikes=1,
        )

        Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="deactivated-123",
            review_deck="Not bad",
            review_description="It was okay",
            score=3,
            likes=2,
            dislikes=3,
        )

    def test_can_get_reviews(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("reviews", data)
        self.assertEqual(len(data["reviews"]), 2)

    def test_hides_deactivated_users(self):
        response = self.client.get(self.url, secure=True)
        data = response.json()

        deactivated_reviews = [r for r in data["reviews"] if r["reviewer"] == "inactive-user"]
        self.assertTrue(len(deactivated_reviews) > 0)

    def test_shows_dates_in_dd_mm_yyyy(self):
        response = self.client.get(self.url, secure=True)
        data = response.json()

        for review in data["reviews"]:
            self.assertRegex(review["date_added"], r"\d{2}/\d{2}/\d{4}")

    @patch("playstyle_compass.views.Review.objects.filter")
    def test_masks_invalid_user_id(self, mock_filter):
        mock_review = MagicMock()
        mock_review.id = 1
        mock_review.reviewers = "tester"
        mock_review.review_deck = "Test deck"
        mock_review.review_description = "Test desc"
        mock_review.score = 5
        mock_review.likes = 0
        mock_review.dislikes = 0
        mock_review.date_added = now()
        mock_review.user_id = "-65123"

        mock_filter.return_value = [mock_review]

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        invalid_user_reviews = [r for r in data["reviews"] if r["user_id"] == "invalid_user"]
        self.assertTrue(len(invalid_user_reviews) > 0)


class LikeReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234", title="Game", description="desc",
            genres="Action", platforms="PC", image="img.png",
            videos="none", concepts="Concept"
        )

        self.review = Review.objects.create(
            game=self.game,
            user=self.other_user,
            reviewers="someone",
            review_deck="Deck",
            review_description="Desc",
            score=3,
            likes=0,
            dislikes=0,
        )

        self.url = reverse("playstyle_compass:like")

    def test_can_like_review(self):
        self.review.liked_by = ""
        self.review.save()
        
        response = self.client.post(self.url, {"review_id": self.review.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("likes", data)
        self.assertEqual(data["likes"], 1)

    def test_can_unlike_review(self):
        self.review.liked_by = ""
        self.review.save()
        
        self.review.add_like(self.user.id)
        response = self.client.post(self.url, {"review_id": self.review.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["likes"], 0)

    def test_cannot_like_own_review(self):
        own_review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="me",
            review_deck="Deck",
            review_description="Desc",
            score=5,
        )
        response = self.client.post(self.url, {"review_id": own_review.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cannot like your own review", data["message"].lower())

    def test_invalid_review_id(self):
        response = self.client.post(self.url, {"review_id": 9999}, secure=True)
        self.assertEqual(response.status_code, 404)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url, {"review_id": self.review.id}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DislikeReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234", title="Game", description="desc",
            genres="Action", platforms="PC", image="img.png",
            videos="none", concepts="Concept"
        )

        self.review = Review.objects.create(
            game=self.game,
            user=self.other_user,
            reviewers="someone",
            review_deck="Deck",
            review_description="Desc",
            score=3,
            likes=0,
            dislikes=0,
        )

        self.url = reverse("playstyle_compass:dislike")

    def test_can_dislike_review(self):
        self.review.disliked_by = ""
        self.review.save()

        response = self.client.post(self.url, {"review_id": self.review.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("dislikes", data)
        self.assertEqual(data["dislikes"], 1)

    def test_can_undislike_review(self):
        self.review.disliked_by = ""
        self.review.save()

        self.review.add_dislike(self.user.id)
        response = self.client.post(self.url, {"review_id": self.review.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["dislikes"], 0)

    def test_cannot_dislike_own_review(self):
        own_review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="me",
            review_deck="Deck",
            review_description="Desc",
            score=5,
        )
        response = self.client.post(self.url, {"review_id": own_review.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cannot dislike your own review", data["message"].lower())

    def test_invalid_review_id(self):
        response = self.client.post(self.url, {"review_id": 9999}, secure=True)
        self.assertEqual(response.status_code, 404)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url, {"review_id": self.review.id}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DeleteReviewsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept"
        )

        self.review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="someone",
            review_deck="Deck",
            review_description="Desc",
            score=3,
        )

        self.url = reverse("playstyle_compass:delete_reviews", args=[self.game.guid])

    def test_can_delete_review(self):
        response = self.client.post(self.url, {"next": "/"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("successfully deleted", str(messages_list[0].message).lower())

    def test_cannot_delete_nonexistent_review(self):
        self.review.delete()
        response = self.client.post(self.url, {"next": "/"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("haven't written any reviews", str(messages_list[0].message).lower())

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url, {"next": "/"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.headers["Location"])

    def test_redirects_to_index_if_no_next(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("playstyle_compass:index"))


class ViewGameViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept"
        )
        self.url = reverse("playstyle_compass:view_game", args=[self.game.guid])

    def test_can_view_game(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/view_game.html")
        self.assertContains(response, "Test Game")

    def test_game_does_not_exist(self):
        invalid_url = reverse("playstyle_compass:view_game", args=[9999])
        response = self.client.get(invalid_url, secure=True)
        self.assertEqual(response.status_code, 404)


class ShareGameViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.receiver = User.objects.create_user(username="receiveruser", password="testpass")

        self.user.userprofile.profile_name = "TestUser"
        self.user.userprofile.save()
        self.receiver.userprofile.profile_name = "ReceiverUser"
        self.receiver.userprofile.save()

        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept"
        )

        self.url = reverse("playstyle_compass:share_game", args=[self.game.guid])

    def test_can_share_game(self):
        response = self.client.post(self.url, {"receiver_id": self.receiver.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("successfully shared", data["message"].lower())
        self.assertTrue(SharedGame.objects.filter(sender=self.user, receiver=self.receiver, game_id=self.game.guid).exists())

    def test_cannot_share_game_twice(self):
        SharedGame.objects.create(sender=self.user, receiver=self.receiver, game_id=self.game.guid)
        response = self.client.post(self.url, {"receiver_id": self.receiver.id}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("already shared", data["message"].lower())

    def test_missing_receiver_id(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("receiver id not provided", data["message"].lower())

    def test_invalid_request_method(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("invalid request method", data["message"].lower())

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url, {"receiver_id": self.receiver.id}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class ViewGamesSharedViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.user.userprofile.timezone = "UTC"
        self.user.userprofile.save()
        self.client.login(username="testuser", password="testpass")

        self.game1 = Game.objects.create(
            guid="1111",
            title="First Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept"
        )
        self.game2 = Game.objects.create(
            guid="2222",
            title="Second Game",
            description="desc",
            genres="Action",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Concept"
        )

        SharedGame.objects.create(sender=self.other_user, receiver=self.user, game_id=self.game1.guid)
        SharedGame.objects.create(sender=self.user, receiver=self.other_user, game_id=self.game2.guid)

        self.url = reverse("playstyle_compass:games_shared")

    def test_view_received_games(self):
        response = self.client.get(self.url + "?category=received", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/games_shared.html")
        games = response.context["games"]
        self.assertEqual(games.count(), 1)
        self.assertEqual(str(games.first().game_id), self.game1.guid)

    def test_view_sent_games(self):
        response = self.client.get(self.url + "?category=sent", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/games_shared.html")
        games = response.context["games"]
        self.assertEqual(games.count(), 1)
        self.assertEqual(str(games.first().game_id), self.game2.guid)

    def test_sorting_descending(self):
        SharedGame.objects.create(sender=self.other_user, receiver=self.user, game_id="3333")
        SharedGame.objects.create(sender=self.other_user, receiver=self.user, game_id="4444")
        response = self.client.get(self.url + "?category=received&sort_order=desc", secure=True)
        self.assertEqual(response.status_code, 200)
        games = list(response.context["games"])
        timestamps = [game.timestamp for game in games]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_invalid_category_returns_empty(self):
        response = self.client.get(self.url + "?category=invalid", secure=True)
        self.assertEqual(response.status_code, 200)
        games = response.context["games"]
        self.assertEqual(len(games), 0)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)



if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views"])
    sys.exit(bool(failures))
