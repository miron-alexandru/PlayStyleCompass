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
from urllib.parse import urlencode

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.utils.timezone import now, localtime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from playstyle_compass.models import *
from playstyle_compass.forms import *
from playstyle_compass.views import get_filtered_games
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
        self.url = reverse('playstyle_compass:search_franchises')

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


class DeleteSharedGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
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

        self.received_game = SharedGame.objects.create(
            sender=self.other_user, receiver=self.user, game_id=self.game1.guid
        )
        self.sent_game = SharedGame.objects.create(
            sender=self.user, receiver=self.other_user, game_id=self.game2.guid
        )
        self.both_deleted_game = SharedGame.objects.create(
            sender=self.user,
            receiver=self.other_user,
            game_id="3333",
            is_deleted_by_receiver=True,
            is_deleted_by_sender=True,
        )

        self.url = reverse("playstyle_compass:delete_shared_games")

    def test_delete_received(self):
        params = urlencode({"category": "received", "sort_order": "asc"})
        response = self.client.post(
            f"{self.url}?{params}",
            {"received_games[]": [self.received_game.id]},
            secure=True,
        )
        self.received_game.refresh_from_db()
        self.assertTrue(self.received_game.is_deleted_by_receiver)
        expected_url = reverse("playstyle_compass:games_shared") + f"?{params}"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_delete_sent(self):
        params = urlencode({"category": "sent", "sort_order": "desc"})
        response = self.client.post(
            f"{self.url}?{params}",
            {"shared_games[]": [self.sent_game.id]},
            secure=True,
        )
        self.sent_game.refresh_from_db()
        self.assertTrue(self.sent_game.is_deleted_by_sender)
        expected_url = reverse("playstyle_compass:games_shared") + f"?{params}"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_delete_both(self):
        params = urlencode({"category": "both", "sort_order": "desc"})
        response = self.client.post(
            f"{self.url}?{params}",
            {
                "received_games[]": [self.received_game.id],
                "shared_games[]": [self.sent_game.id],
            },
            secure=True,
        )
        self.received_game.refresh_from_db()
        self.sent_game.refresh_from_db()
        self.assertTrue(self.received_game.is_deleted_by_receiver)
        self.assertTrue(self.sent_game.is_deleted_by_sender)
        expected_url = reverse("playstyle_compass:games_shared") + f"?{params}"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_removes_deleted_games(self):
        response = self.client.post(self.url, {}, secure=True)
        exists = SharedGame.objects.filter(id=self.both_deleted_game.id).exists()
        self.assertFalse(exists)
        expected_url = reverse("playstyle_compass:games_shared") + "?category=&sort_order="
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_needs_login(self):
        self.client.logout()
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


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


class PlayHistoriesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.different_user = User.objects.create_user(username="diffuser", password="testpass")

        self.user.userpreferences.gaming_history = "Long"
        self.user.userpreferences.save()

        self.other_user.userpreferences.gaming_history = "Long"
        self.other_user.userpreferences.save()

        self.different_user.userpreferences.gaming_history = "Short"
        self.different_user.userpreferences.save()

        self.client.login(username="testuser", password="testpass")
        self.url = reverse("playstyle_compass:play_histories")

    def test_view_loads(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "misc/play_histories.html")

    def test_shows_similar_gaming_history(self):
        response = self.client.get(self.url, secure=True)
        users = response.context["similar_user_gaming_history"]
        self.assertIn(self.other_user.userpreferences, users)

    def test_hides_different_gaming_history(self):
        response = self.client.get(self.url, secure=True)
        users = response.context["similar_user_gaming_history"]
        self.assertNotIn(self.different_user.userpreferences, users)

    def test_gives_user_preferences(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.context["user_preferences"], self.user.userpreferences)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class ViewFranchisesViewTest(TestCase):
    def setUp(self):
        self.url = reverse("playstyle_compass:view_franchises")
        Franchise.objects.create(title="Zelda", games_count=10)
        Franchise.objects.create(title="Mario", games_count=5)
        Franchise.objects.create(title="Metroid", games_count=7)

    def test_view_loads(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/franchise_list.html")

    def test_shows_all_franchises(self):
        response = self.client.get(self.url, secure=True)
        franchises = response.context["franchises"].object_list
        self.assertEqual(len(franchises), 3)

    def test_sorts_alphabetically_ascending(self):
        response = self.client.get(self.url + "?sort_order=asc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        titles = [f.title for f in franchises]
        self.assertEqual(titles, sorted(titles))

    def test_sorts_alphabetically_descending(self):
        response = self.client.get(self.url + "?sort_order=desc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        titles = [f.title for f in franchises]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_sorts_by_games_count_ascending(self):
        response = self.client.get(self.url + "?sort_order=games_asc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        games_counts = [f.games_count for f in franchises]
        self.assertEqual(games_counts, sorted(games_counts))

    def test_sorts_by_games_count_descending(self):
        response = self.client.get(self.url + "?sort_order=games_desc", secure=True)
        franchises = list(response.context["franchises"].object_list)
        games_counts = [f.games_count for f in franchises]
        self.assertEqual(games_counts, sorted(games_counts, reverse=True))


class ViewFranchiseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.franchise = Franchise.objects.create(title="Awesome Franchise", games_count=5)
        self.url = reverse("playstyle_compass:franchise", args=[self.franchise.id])

    def test_can_view_franchise(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "franchises/view_franchise.html")
        franchise = response.context["franchise"]
        self.assertEqual(franchise, self.franchise)
        self.assertIn(self.franchise.title, response.context["page_title"])

    def test_404_if_not_found(self):
        invalid_url = reverse("playstyle_compass:franchise", args=[999])
        response = self.client.get(invalid_url, secure=True)
        self.assertEqual(response.status_code, 404)


class ViewCharactersViewTest(TestCase):
    def setUp(self):
        self.char1 = Character.objects.create(name="Alpha Character")
        self.char2 = Character.objects.create(name="Bravo Character")
        self.char3 = Character.objects.create(name="Charlie Character")
        self.url = reverse("playstyle_compass:characters")

    def test_shows_all_characters(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "characters/characters.html")
        characters = list(response.context["characters"])
        self.assertEqual(len(characters), 3)

    def test_sorts_characters_ascending(self):
        response = self.client.get(self.url + "?sort_order=asc", secure=True)
        characters = list(response.context["characters"])
        names = [c.name for c in characters]
        self.assertEqual(names, sorted(names))

    def test_sorts_characters_descending(self):
        response = self.client.get(self.url + "?sort_order=desc", secure=True)
        characters = list(response.context["characters"])
        names = [c.name for c in characters]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_invalid_sort_order_defaults(self):
        response = self.client.get(self.url + "?sort_order=invalid", secure=True)
        self.assertEqual(response.status_code, 200)
        characters = list(response.context["characters"])
        self.assertEqual(len(characters), 3)

class GameCharacterViewTest(TestCase):
    def setUp(self):
        self.character = Character.objects.create(name="Test Character")
        self.url = reverse("playstyle_compass:character", args=[self.character.id])

    def test_shows_character_page(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "characters/game_character.html")
        self.assertEqual(response.context["character"], self.character)
        self.assertContains(response, self.character.name)

    def test_returns_404_for_missing_character(self):
        url = reverse("playstyle_compass:character", args=[9999])
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 404)


class SearchCharactersViewTest(TestCase):
    def setUp(self):
        self.character1 = Character.objects.create(name="Aloy")
        self.character2 = Character.objects.create(name="Arthur Morgan")
        self.url = reverse("playstyle_compass:search_characters")

    def test_can_find_character(self):
        response = self.client.get(self.url, {"query": "Aloy"}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "characters/search_characters.html")
        characters = response.context["characters"]
        self.assertIn(self.character1, characters)
        self.assertNotIn(self.character2, characters)
        self.assertContains(response, "Aloy")

    def test_short_query_is_bad(self):
        response = self.client.get(self.url, {"query": "A"}, secure=True)
        self.assertEqual(response.status_code, 400)

    def test_empty_results(self):
        response = self.client.get(self.url, {"query": "NothingHere"}, secure=True)
        self.assertEqual(response.status_code, 200)
        characters = response.context["characters"]
        self.assertEqual(len(characters), 0)


class AutocompleteCharactersViewTest(TestCase):
    def setUp(self):
        self.character1 = Character.objects.create(name="Aloy")
        self.character2 = Character.objects.create(name="Arthur Morgan")
        self.character3 = Character.objects.create(name="Kratos")
        self.url = reverse("playstyle_compass:autocomplete_characters")

    def test_returns_matches(self):
        response = self.client.get(self.url, {"query": "Ar"}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = [item["name"] for item in data["results"]]
        self.assertIn("Arthur Morgan", results)
        self.assertNotIn("Aloy", results)
        self.assertNotIn("Kratos", results)

    def test_returns_empty_when_no_match(self):
        response = self.client.get(self.url, {"query": "Zelda"}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], [])

    def test_returns_empty_for_blank_query(self):
        response = self.client.get(self.url, {"query": ""}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], [])


class ViewSingleplayerGamesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

        self.game = Game.objects.create(
            guid="1111",
            title="Solo Adventure",
            description="desc",
            genres="RPG",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Single-Player Only",
        )
        GameModes.objects.create(game_id=self.game.guid, game_mode="Singleplayer")
        self.url = reverse("playstyle_compass:singleplayer_games")

    def test_shows_singleplayer_games(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/singleplayer_games.html")
        self.assertIn("Solo Adventure", response.content.decode())

class ViewMultiplayerGamesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

        self.game = Game.objects.create(
            guid="2222",
            title="Party Brawler",
            description="desc",
            genres="Fighting",
            platforms="PC",
            image="img.png",
            videos="none",
            concepts="Split-Screen Multiplayer",
        )
        GameModes.objects.create(game_id=self.game.guid, game_mode="Multiplayer")
        self.url = reverse("playstyle_compass:multiplayer_games")

    def test_shows_multiplayer_games(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/multiplayer_games.html")
        self.assertIn("Party Brawler", response.content.decode())


class GameLibraryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_login(self.user)
        self.url = reverse("playstyle_compass:game_library")

        self.game1 = Game.objects.create(
            guid="1",
            title="Space Odyssey",
            genres="Sci-Fi",
            concepts="Exploration",
            themes="Space",
            platforms="PC",
            franchises="Odyssey"
        )
        self.game2 = Game.objects.create(
            guid="2",
            title="Fantasy Quest",
            genres="Fantasy",
            concepts="Adventure",
            themes="Magic",
            platforms="PS5",
            franchises="Quest"
        )

    @patch("playstyle_compass.views.gather_game_attributes", return_value=(["Sci-Fi", "Fantasy"], ["Exploration", "Adventure"], ["Space", "Magic"], ["PC", "PS5"], ["Odyssey", "Quest"]))
    def test_can_show_games(self, mock_gather):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Space Odyssey")
        self.assertContains(response, "Fantasy Quest")

    @patch("playstyle_compass.views.gather_game_attributes", return_value=(["Sci-Fi", "Fantasy"], ["Exploration", "Adventure"], ["Space", "Magic"], ["PC", "PS5"], ["Odyssey", "Quest"]))
    def test_can_filter_by_genre(self, mock_gather):
        query = urlencode({"genres": "Fantasy"})
        response = self.client.get(f"{self.url}?{query}", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fantasy Quest")
        self.assertNotContains(response, "Space Odyssey")

    @patch("playstyle_compass.views.gather_game_attributes", return_value=(["Sci-Fi", "Fantasy"], ["Exploration", "Adventure"], ["Space", "Magic"], ["PC", "PS5"], ["Odyssey", "Quest"]))
    def test_can_sort_games(self, mock_gather):
        query = urlencode({"sort_by": "title_asc"})
        response = self.client.get(f"{self.url}?{query}", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Space Odyssey")
        self.assertContains(response, "Fantasy Quest")


class LatestNewsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_login(self.user)
        self.url = reverse("playstyle_compass:latest_news")

        self.article1 = News.objects.create(
            title="PC Gaming Rising",
            platforms="PC",
            publish_date="2024-01-01"
        )
        self.article2 = News.objects.create(
            title="Console Wars Continue",
            platforms="PS5",
            publish_date="2024-02-01"
        )
        self.article3 = News.objects.create(
            title="VR Gets Bigger",
            platforms="VR",
            publish_date="2024-03-01"
        )

    @patch("playstyle_compass.views.get_associated_platforms", return_value=["PC", "PS5", "VR"])
    def test_shows_all_articles(self, mock_platforms):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PC Gaming Rising")
        self.assertContains(response, "Console Wars Continue")
        self.assertContains(response, "VR Gets Bigger")

    @patch("playstyle_compass.views.get_associated_platforms", return_value=["PC", "PS5", "VR"])
    def test_filters_by_platform(self, mock_platforms):
        response = self.client.get(self.url + "?platforms=PC", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PC Gaming Rising")
        self.assertNotContains(response, "Console Wars Continue")
        self.assertNotContains(response, "VR Gets Bigger")

    @patch("playstyle_compass.views.get_associated_platforms", return_value=["PC", "PS5", "VR"])
    @patch("playstyle_compass.views.sort_articles", side_effect=lambda qs, sort_by: qs.order_by("-publish_date"))
    def test_sorts_articles(self, mock_sort, mock_platforms):
        response = self.client.get(self.url + "?sort_by=publish_date_desc", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PC Gaming Rising")
        self.assertContains(response, "Console Wars Continue")
        self.assertContains(response, "VR Gets Bigger")


class SimilarGamesDirectoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_login(self.user)
        self.url = reverse("playstyle_compass:similar_games_directory")

        Game.objects.create(title="Apex Legends", guid=1234)
        Game.objects.create(title="Zelda", guid=3293)
        Game.objects.create(title="123 Racing", guid=2392)
        Game.objects.create(title="Among Us", guid=2932)

    def test_shows_games_by_letter(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        context = response.context["games_by_letter"]

        self.assertIn("A", context)
        self.assertIn("Z", context)
        self.assertIn("R", context)

        self.assertTrue(any(game.title == "Apex Legends" for game in context["A"]))
        self.assertTrue(any(game.title == "Among Us" for game in context["A"]))
        self.assertTrue(any(game.title == "Zelda" for game in context["Z"]))
        self.assertTrue(any(game.title == "123 Racing" for game in context["R"]))

    def test_uses_right_template(self):
        response = self.client.get(self.url, secure=True)
        self.assertTemplateUsed(response, "games/similar_games_directory.html")


class SimilarGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_login(self.user)

        self.main_game = Game.objects.create(title="Dark Souls", guid=1111)
        self.similar_game1 = Game.objects.create(title="Elden Ring", guid=2222)
        self.similar_game2 = Game.objects.create(title="Bloodborne", guid=3333)

        self.url = reverse("playstyle_compass:similar_games", args=[self.main_game.guid])

    @patch("playstyle_compass.views.get_similar_games")
    def test_shows_similar_games(self, mock_get_similar_games):
        mock_get_similar_games.return_value = Game.objects.filter(
            pk__in=[self.similar_game1.pk, self.similar_game2.pk]
        )

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(context["main_game"], self.main_game)
        self.assertIn(self.similar_game1, context["similar_games"])
        self.assertIn(self.similar_game2, context["similar_games"])

    def test_uses_right_template(self):
        with patch("playstyle_compass.views.get_similar_games") as mock_get_similar_games:
            mock_get_similar_games.return_value = Game.objects.none()
            response = self.client.get(self.url, secure=True)
            self.assertTemplateUsed(response, "games/similar_games.html")


class GetFilteredGamesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.factory = RequestFactory()

        Game.objects.create(title="Singleplayer Game", concepts="Singleplayer", guid=123)
        Game.objects.create(title="Multiplayer Game", concepts="Multiplayer", guid=456)
        Game.objects.create(title="Hybrid Game", concepts="Singleplayer, Multiplayer", guid=789)

    def test_can_filter_games_by_keyword(self):
        request = self.factory.get("/", secure=True)
        request.user = self.user
        
        games, prefs, friends = get_filtered_games(request, "Singleplayer")
        titles = [game.title for game in games]

        self.assertIn("Singleplayer Game", titles)
        self.assertIn("Hybrid Game", titles)
        self.assertNotIn("Multiplayer Game", titles)

    def test_returns_empty_if_no_match(self):
        request = self.factory.get("/", secure=True)
        request.user = self.user
        
        games, prefs, friends = get_filtered_games(request, "Nonexistent")
        self.assertEqual(list(games), [])


class GameCategoryViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_login(self.user)

        Game.objects.create(title="Open World Game", concepts="Open World", guid=1)
        Game.objects.create(title="Linear Game", concepts="Linear Gameplay", guid=2)
        Game.objects.create(title="Indie Darling", concepts="Indie", guid=3)
        Game.objects.create(title="Steam Hit", concepts="Steam", guid=4)
        Game.objects.create(title="F2P Blast", concepts="Free to Play", guid=5)
        Game.objects.create(title="VR Madness", concepts="Virtual Reality", guid=6)
        Game.objects.create(title="Beginner's Luck", is_casual=True, guid=7)

    def test_open_world_page(self):
        response = self.client.get(reverse("playstyle_compass:open_world_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/open_world_games.html")

    def test_linear_gameplay_page(self):
        response = self.client.get(reverse("playstyle_compass:linear_gameplay_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/linear_gameplay_games.html")

    def test_indie_page(self):
        response = self.client.get(reverse("playstyle_compass:indie_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/indie_games.html")

    def test_steam_page(self):
        response = self.client.get(reverse("playstyle_compass:steam_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/steam_games.html")

    def test_free_to_play_page(self):
        response = self.client.get(reverse("playstyle_compass:free_to_play_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/free_to_play_games.html")

    def test_vr_page(self):
        response = self.client.get(reverse("playstyle_compass:vr_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/vr_games.html")

    def test_beginner_page(self):
        response = self.client.get(reverse("playstyle_compass:beginner_games"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/beginner_games.html")


class CreateGameListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_login(self.user)
        self.url = reverse("playstyle_compass:create_game_list")

        self.game1 = Game.objects.create(title="Game One", guid="1111")
        self.game2 = Game.objects.create(title="Game Two", guid="2222")

    def test_shows_form(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/create_game_list.html")
        self.assertIn("form", response.context)

    def test_can_create_list(self):
        post_data = {
            "title": "My New Game List",
            "description": "A cool list of games.",
            "games": [self.game1.pk, self.game2.pk],
            "additional_games": "Extra Game 1, Extra Game 2",
            "is_public": True,
        }
        response = self.client.post(self.url, post_data, secure=True)
        self.assertEqual(response.status_code, 302)

        game_list = GameList.objects.get(title="My New Game List")
        self.assertEqual(game_list.owner, self.user)
        self.assertEqual(game_list.description, "A cool list of games.")
        self.assertListEqual(game_list.game_guids, [self.game1.guid, self.game2.guid])
        self.assertTrue(game_list.is_public)

    def test_invalid_form_shows_errors(self):
        response = self.client.post(self.url, {"title": ""}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/create_game_list.html")
        self.assertTrue(response.context["form"].errors)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class EditGameListViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.game1 = Game.objects.create(title="Game One", guid="1111")
        self.game2 = Game.objects.create(title="Game Two", guid="2222")
        self.client.force_login(self.owner)

        self.game_list = GameList.objects.create(
            title="Original List",
            description="Original Description",
            owner=self.owner,
            game_guids=[self.game1.guid],
            additional_games="Extra Game",
            is_public=False,
        )
        self.url = reverse("playstyle_compass:edit_game_list", args=[self.game_list.pk])

    def test_can_load_form(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/edit_game_list.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["game_list"], self.game_list)

    def test_can_update_game_list(self):
        self.client.force_login(self.owner)
        post_data = {
            "title": "Updated List",
            "description": "Updated description",
            "games": [self.game1.pk, self.game2.pk],
            "additional_games": "Another Extra Game",
            "is_public": True,
        }
        response = self.client.post(self.url, post_data, secure=True)
        self.assertEqual(response.status_code, 302)

        self.game_list.refresh_from_db()
        self.assertEqual(self.game_list.title, "Updated List")
        self.assertEqual(self.game_list.description, "Updated description")
        self.assertListEqual(self.game_list.game_guids, [self.game1.guid, self.game2.guid])
        self.assertEqual(self.game_list.additional_games, "Another Extra Game")
        self.assertTrue(self.game_list.is_public)

    def test_cant_edit_other_users_list(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("playstyle_compass:game_list_detail", args=[self.game_list.pk]), response.url)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DeleteGameListViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.game = Game.objects.create(title="Game One", guid="g1")
        self.game_list = GameList.objects.create(
            title="My List",
            description="A sample list",
            owner=self.owner,
            game_guids=[self.game.guid],
            additional_games="Extra",
            is_public=True,
        )
        self.url = reverse("playstyle_compass:delete_game_list", args=[self.game_list.pk])
        self.redirect_url = reverse("playstyle_compass:user_game_lists", args=[self.owner.id])

    def test_can_delete_own_list(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.redirect_url)
        self.assertFalse(GameList.objects.filter(pk=self.game_list.pk).exists())

    def test_cant_delete_others_list(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("playstyle_compass:game_list_detail", args=[self.game_list.pk]), response.url)
        self.assertTrue(GameList.objects.filter(pk=self.game_list.pk).exists())

    def test_redirects_if_not_logged_in(self):
        self.client.force_login(self.owner)
        self.client.logout()
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DeleteAllGameListsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")

        self.list1 = GameList.objects.create(title="List 1", owner=self.user)
        self.list2 = GameList.objects.create(title="List 2", owner=self.user)
        GameList.objects.create(title="Other List", owner=self.other)

        self.url = reverse("playstyle_compass:delete_all_game_lists")
        self.redirect_url = reverse("playstyle_compass:user_game_lists", args=[self.user.id])

    def test_deletes_all_lists(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.redirect_url)

        self.assertFalse(GameList.objects.filter(owner=self.user).exists())
        self.assertTrue(GameList.objects.filter(owner=self.other).exists())

    def test_does_nothing_if_no_lists(self):
        self.client.force_login(self.user)
        GameList.objects.filter(owner=self.user).delete()

        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.redirect_url)
        self.assertFalse(GameList.objects.filter(owner=self.user).exists())

    def test_redirects_if_not_logged_in(self):
        self.client.force_login(self.user)
        self.client.logout()
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class GameListDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.game = Game.objects.create(title="Sample Game", guid=1234)
        self.game_list = GameList.objects.create(
            title="My List",
            owner=self.user,
            game_guids=[self.game.guid],
            additional_games="Extra1,Extra2"
        )
        self.url = reverse("playstyle_compass:game_list_detail", args=[self.game_list.pk])

    def test_loads_list_detail(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/game_list_detail.html")

        context = response.context
        self.assertEqual(context["game_list"], self.game_list)
        self.assertEqual(context["additional_games"], ["Extra1", "Extra2"])
        games_page = context["games"]
        self.assertEqual(games_page.paginator.count, 1)
        self.assertEqual(context["user_preferences"], self.user.userpreferences)
        self.assertTrue("form" in context)
        self.assertTrue("review" in context)
        self.assertTrue("comment_form" in context)
        self.assertTrue("comments" in context)

    def test_returns_404_for_invalid_id(self):
        invalid_url = reverse("playstyle_compass:game_list_detail", args=[999])
        response = self.client.get(invalid_url, secure=True)
        self.assertEqual(response.status_code, 404)

    def test_shows_reviews_and_comments(self):
        self.client.force_login(self.user)

        ListReview.objects.create(
            game_list=self.game_list,
            user=self.user,
            review_text="Great list!",
            rating=5
        )
        ListComment.objects.create(
            game_list=self.game_list,
            user=self.user,
            text="Nice!"
        )

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(len(context["reviews"]), 1)
        self.assertEqual(len(context["comments"]), 1)


class ShareGameListViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.friend1 = User.objects.create_user(username="friend1", password="testpass")
        self.friend2 = User.objects.create_user(username="friend2", password="testpass")

        self.game_list = GameList.objects.create(title="My List", owner=self.owner)
        self.url = reverse("playstyle_compass:share_game_list", args=[self.game_list.pk])

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_can_open_share_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/share_game_list.html")
        self.assertEqual(response.context["game_list"], self.game_list)

    def test_can_share_with_friends(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            self.url,
            data={"shared_with": [self.friend1.pk, self.friend2.pk]},
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("playstyle_compass:game_list_detail", args=[self.game_list.pk]))

        self.game_list.refresh_from_db()
        self.assertIn(self.friend1, self.game_list.shared_with.all())
        self.assertIn(self.friend2, self.game_list.shared_with.all())
        self.assertIn(str(self.owner.pk), self.game_list.shared_by)
        self.assertIn(str(self.friend1.pk), self.game_list.shared_by[str(self.owner.pk)])
        self.assertIn(str(self.friend2.pk), self.game_list.shared_by[str(self.owner.pk)])

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully shared" in str(m) for m in messages))

    def test_sharing_with_nobody_fails(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, data={}, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "At least one friend must be selected", status_code=400)


class UserGameListsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        now = timezone.now()

        self.list1 = GameList.objects.create(
            title="Alpha",
            owner=self.user,
            game_guids=["g1", "g2"],
            additional_games="Extra1,Extra2",
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1),
        )
        self.list2 = GameList.objects.create(
            title="Bravo",
            owner=self.user,
            game_guids=["g3"],
            additional_games="Extra3",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
        )
        self.list3 = GameList.objects.create(
            title="Charlie",
            owner=self.user,
            game_guids=[],
            additional_games="",
            created_at=now - timedelta(days=1),
            updated_at=now,
        )

        self.list1.liked_by.add(self.user)
        self.list1.shared_with.add(self.user)
        self.list1.favorites.add(self.user)

        self.list2.liked_by.add(self.user)
        self.list2.shared_with.add(self.user)

        self.url = reverse("playstyle_compass:user_game_lists", args=[self.user.id])

    def test_can_load_lists(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/user_game_lists.html")
        self.assertEqual(response.context["list_user"], self.user)
        self.assertIn(self.list1, response.context["game_lists"])
        self.assertIn(self.list2, response.context["game_lists"])
        self.assertIn(self.list3, response.context["game_lists"])

    def test_sort_by_title_asc(self):
        response = self.client.get(self.url + "?sort_by=title&order=asc", secure=True)
        titles = [gl.title for gl in response.context["game_lists"]]
        self.assertEqual(titles, ["Alpha", "Bravo", "Charlie"])

    def test_sort_by_title_desc(self):
        response = self.client.get(self.url + "?sort_by=title&order=desc", secure=True)
        titles = [gl.title for gl in response.context["game_lists"]]
        self.assertEqual(titles, ["Charlie", "Bravo", "Alpha"])

    def test_sort_by_total_games(self):
        response = self.client.get(self.url + "?sort_by=total_games&order=desc", secure=True)
        counts = [gl.total_games for gl in response.context["game_lists"]]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_sort_by_created_at(self):
        response = self.client.get(self.url + "?sort_by=created_at&order=asc", secure=True)
        created = [gl.created_at for gl in response.context["game_lists"]]
        self.assertEqual(created, sorted(created))

    def test_sort_by_updated_at(self):
        response = self.client.get(self.url + "?sort_by=updated_at&order=desc", secure=True)
        updated = [gl.updated_at for gl in response.context["game_lists"]]
        self.assertEqual(updated, sorted(updated, reverse=True))

    def test_sort_by_like_count(self):
        response = self.client.get(self.url + "?sort_by=like_count&order=desc", secure=True)
        likes = [gl.like_count for gl in response.context["game_lists"]]
        self.assertEqual(likes, sorted(likes, reverse=True))

    def test_sort_by_share_count(self):
        response = self.client.get(self.url + "?sort_by=share_count&order=desc", secure=True)
        shares = [gl.share_count for gl in response.context["game_lists"]]
        self.assertEqual(shares, sorted(shares, reverse=True))

    def test_sort_by_activity_level(self):
        response = self.client.get(self.url + "?sort_by=activity_level&order=desc", secure=True)
        activity = [
            gl.share_count + gl.like_count + gl.review_count
            for gl in response.context["game_lists"]
        ]
        self.assertEqual(activity, sorted(activity, reverse=True))

    def test_invalid_user_gives_404(self):
        bad_url = reverse("playstyle_compass:user_game_lists", args=[9999])
        response = self.client.get(bad_url, secure=True)
        self.assertEqual(response.status_code, 404)


class SharedGameListsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.friend = User.objects.create_user(username="friend", password="testpass")

        self.shared_by_user = GameList.objects.create(
            owner=self.user,
            title="Shared By Me",
            game_guids=["4212", "3134"],
            shared_by={str(self.user.id): [str(self.friend.id)]},
        )
        self.shared_by_user.shared_with.add(self.friend)

        self.shared_with_user = GameList.objects.create(
            owner=self.friend,
            title="Shared With Me",
            game_guids=["3242"],
            shared_by={str(self.friend.id): [str(self.user.id)]},
        )
        self.shared_with_user.shared_with.add(self.user)

        self.url = reverse("playstyle_compass:shared_game_lists")

    def test_login_required(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_can_see_lists_shared_with_me(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + "?view=received", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game_list/shared_game_lists.html")
        game_lists = response.context["game_lists"]
        self.assertIn(self.shared_with_user, game_lists)
        self.assertNotIn(self.shared_by_user, game_lists)
        self.assertEqual(response.context["view_type"], "received")

        gl_from_context = next(gl for gl in game_lists if gl.pk == self.shared_with_user.pk)
        self.assertTrue(hasattr(gl_from_context, "shared_by_users"))
        self.assertEqual(list(gl_from_context.shared_by_users), [self.friend])

    def test_can_see_lists_i_shared_with_others(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + "?view=shared", secure=True)

        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertIn(self.shared_by_user, game_lists)
        self.assertNotIn(self.shared_with_user, game_lists)
        self.assertEqual(response.context["view_type"], "shared")

    def test_sort_by_title_asc(self):
        self.client.force_login(self.user)
        gl = GameList.objects.create(
            owner=self.friend,
            title="AAA List",
            game_guids=["3243"],
            shared_by={str(self.friend.id): [str(self.user.id)]},
        )
        gl.shared_with.add(self.user)

        response = self.client.get(self.url + "?view=received&sort_by=title&order=asc", secure=True)
        titles = [gl.title for gl in response.context["game_lists"]]
        self.assertEqual(titles, sorted(titles, key=str.lower))

    def test_sort_by_total_games_desc(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + "?view=received&sort_by=total_games&order=desc", secure=True)
        totals = [gl.total_games for gl in response.context["game_lists"]]
        self.assertEqual(totals, sorted(totals, reverse=True))

class LikeGameListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.game_list = GameList.objects.create(
            owner=self.user,
            title="Cool Games",
            game_guids=["g1", "g2"],
        )
        self.url = reverse("playstyle_compass:like_game_list", args=[self.game_list.id])

    def test_can_like_game_list(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["liked"])
        self.assertEqual(data["like_count"], 1)
        self.assertIn(self.user, self.game_list.liked_by.all())

    def test_can_unlike_game_list(self):
        self.game_list.liked_by.add(self.user)
        self.client.force_login(self.user)

        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertFalse(data["liked"])
        self.assertEqual(data["like_count"], 0)
        self.assertNotIn(self.user, self.game_list.liked_by.all())

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

class ReviewGameListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="testpass")
        self.user.userprofile.profile_name = "CoolReviewer"
        self.user.userprofile.save()

        self.game_list = GameList.objects.create(
            owner=self.user,
            title="My Favorite Games",
            game_guids=["12421", "43232"]
        )

        self.url = reverse("playstyle_compass:review_game_list", args=[self.game_list.id])
        self.valid_data = {
            "title": "Amazing List",
            "rating": 5,
            "review_text": "This list has excellent choices!"
        }

    def test_can_create_review(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.valid_data, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["title"], self.valid_data["title"])
        self.assertEqual(data["rating"], self.valid_data["rating"])
        self.assertEqual(data["review_text"], self.valid_data["review_text"])
        self.assertEqual(data["author"], self.user.userprofile.profile_name)

        self.assertEqual(ListReview.objects.count(), 1)
        review = ListReview.objects.first()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.game_list, self.game_list)

    def test_can_update_review(self):
        old_review = ListReview.objects.create(
            user=self.user,
            game_list=self.game_list,
            title="Old Title",
            rating=2,
            review_text="Old review."
        )

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.valid_data, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        updated_review = ListReview.objects.get(pk=old_review.pk)

        self.assertEqual(updated_review.title, self.valid_data["title"])
        self.assertEqual(updated_review.rating, self.valid_data["rating"])
        self.assertEqual(updated_review.review_text, self.valid_data["review_text"])
        self.assertEqual(data["review_id"], updated_review.id)

    def test_returns_form_errors(self):
        self.client.force_login(self.user)
        invalid_data = {
            "title": "",
            "rating": "",
            "review_text": ""
        }
        response = self.client.post(self.url, data=invalid_data, secure=True)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("errors", data)
        self.assertIn("title", data["errors"])
        self.assertIn("rating", data["errors"])

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, data=self.valid_data, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class EditGameListReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author", password="testpass")
        self.user.userprofile.profile_name = "AuthorUser"
        self.user.userprofile.save()

        self.other_user = User.objects.create_user(username="not_author", password="testpass")

        self.game_list = GameList.objects.create(
            owner=self.user,
            title="Best RPGs",
            game_guids=["g1", "g2"]
        )

        self.review = ListReview.objects.create(
            user=self.user,
            game_list=self.game_list,
            title="Original Title",
            rating=4,
            review_text="Original content"
        )

        self.url = reverse("playstyle_compass:edit_game_list_review", args=[self.review.id])

    def test_can_edit_own_review(self):
        self.client.force_login(self.user)
        data = {
            "title": "Updated Title",
            "rating": 5,
            "review_text": "Much improved review"
        }
        response = self.client.post(self.url, data=data, secure=True)
        self.assertEqual(response.status_code, 200)

        self.review.refresh_from_db()
        self.assertEqual(self.review.title, data["title"])
        self.assertEqual(self.review.rating, data["rating"])
        self.assertEqual(self.review.review_text, data["review_text"])

        response_data = response.json()
        self.assertEqual(response_data["title"], data["title"])
        self.assertEqual(response_data["author"], self.user.userprofile.profile_name)

    def test_returns_form_errors_on_invalid_input(self):
        self.client.force_login(self.user)
        data = {"title": "", "rating": "", "review_text": ""}
        response = self.client.post(self.url, data=data, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())
        self.assertIn("title", response.json()["errors"])

    def test_cannot_edit_review_of_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url, data={
            "title": "Hacked!",
            "rating": 1,
            "review_text": "This shouldn't work"
        }, secure=True)
        self.assertEqual(response.status_code, 404)

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, data={
            "title": "Unauth",
            "rating": 2,
            "review_text": "Anonymous edit"
        }, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DeleteGameListReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author", password="testpass")
        self.other_user = User.objects.create_user(username="not_author", password="testpass")

        self.game_list = GameList.objects.create(
            owner=self.user,
            title="My Game List",
            game_guids=["abc123"]
        )

        self.review = ListReview.objects.create(
            user=self.user,
            game_list=self.game_list,
            title="Solid List",
            rating=4,
            review_text="Nice mix of games."
        )

        self.url = reverse("playstyle_compass:delete_game_list_review", args=[self.review.id])

    def test_can_delete_own_review(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Review deleted successfully!")
        self.assertFalse(ListReview.objects.filter(id=self.review.id).exists())

    def test_cannot_delete_someone_elses_review(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ListReview.objects.filter(id=self.review.id).exists())

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_only_allows_post_requests(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 405)


class LikeGameListReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.author = User.objects.create_user(username="author", password="testpass")

        self.game_list = GameList.objects.create(
            owner=self.author,
            title="List to Review",
            game_guids=["game1"]
        )

        self.review = ListReview.objects.create(
            user=self.author,
            game_list=self.game_list,
            title="Cool List",
            rating=4,
            review_text="Really enjoyed these games."
        )

        self.url = reverse("playstyle_compass:like_list_review", args=[self.review.id])

    def test_can_like_review(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user in self.review.liked_by.all())

        data = response.json()
        self.assertTrue(data["liked"])
        self.assertEqual(data["like_count"], 1)
        self.assertEqual(str(data["review_id"]), str(self.review.id))

    def test_can_unlike_review(self):
        self.review.liked_by.add(self.user)

        self.client.force_login(self.user)
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user in self.review.liked_by.all())

        data = response.json()
        self.assertFalse(data["liked"])
        self.assertEqual(data["like_count"], 0)

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class ReviewedGameListsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.other_user = User.objects.create_user(username="user2", password="testpass")

        self.game_list1 = GameList.objects.create(owner=self.user, title="User1 List", game_guids=["g1", "g2"])
        self.game_list2 = GameList.objects.create(owner=self.other_user, title="User2 List", game_guids=["g3"])

        self.review1 = ListReview.objects.create(
            user=self.user,
            game_list=self.game_list1,
            title="Nice list",
            rating=4,
            review_text="Good games."
        )
        self.review2 = ListReview.objects.create(
            user=self.other_user,
            game_list=self.game_list2,
            title="Other list review",
            rating=5,
            review_text="Great picks."
        )

    def test_can_view_own_reviewed_lists(self):
        self.client.force_login(self.user)
        url = reverse("playstyle_compass:reviewed_game_lists")
        response = self.client.get(url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User1 List")
        self.assertNotContains(response, "User2 List")

        context = response.context
        self.assertEqual(context["list_user"], self.user)
        self.assertFalse(context["other_user"])

    def test_can_view_another_users_reviews(self):
        self.client.force_login(self.user)
        url = reverse("playstyle_compass:reviewed_game_lists_with_id", args=[self.other_user.id])
        response = self.client.get(url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User2 List")
        self.assertNotContains(response, "User1 List")

        context = response.context
        self.assertEqual(context["list_user"], self.other_user)
        self.assertTrue(context["other_user"])

    def test_redirects_if_not_logged_in(self):
        url = reverse("playstyle_compass:reviewed_game_lists")
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class PrivacySettingsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("playstyle_compass:privacy_settings")

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


    def test_page_loads_for_logged_in_user(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "preferences/privacy_settings.html")
        self.assertContains(response, "Privacy Settings")

    def test_can_update_settings(self):
        self.client.login(username="testuser", password="password")
        prefs = UserPreferences.objects.get(user=self.user)

        data = {
            "show_in_queue": False,
            "show_reviews": False,
            "show_favorites": True,
        }

        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response.url)

        prefs.refresh_from_db()
        self.assertFalse(prefs.show_in_queue)
        self.assertFalse(prefs.show_reviews)
        self.assertTrue(prefs.show_favorites)


class ExploreGameListsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("playstyle_compass:explore_game_lists")

        self.list1 = GameList.objects.create(
            owner=self.user, title="First", game_guids=[], is_public=True
        )
        self.list2 = GameList.objects.create(
            owner=self.user, title="Second", game_guids=["4341", "124124"], is_public=True
        )
        self.list3 = GameList.objects.create(
            owner=self.user, title="Third", game_guids=["4322"], is_public=False
        )

    def test_shows_only_public_lists(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First")
        self.assertContains(response, "Second")
        self.assertNotContains(response, "Third")

    def test_sorts_by_title_asc(self):
        response = self.client.get(self.url + "?sort_by=title&order=asc", secure=True)
        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertEqual([g.title for g in game_lists], ["First", "Second"])

    def test_sorts_by_total_games_desc(self):
        response = self.client.get(self.url + "?sort_by=total_games&order=desc", secure=True)
        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertEqual([g.title for g in game_lists], ["Second", "First"])

    def test_default_sort_is_created_at_desc(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertEqual([g.title for g in game_lists], ["Second", "First"])

    def test_handles_invalid_sort_field(self):
        response = self.client.get(self.url + "?sort_by=invalid&order=desc", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First")

class DeleteListCommentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")
        self.game_list = GameList.objects.create(
            owner=self.user, title="Sample List", is_public=True
        )
        self.comment = ListComment.objects.create(
            user=self.user,
            game_list=self.game_list,
            text="Nice list!",
            created_at=timezone.now()
        )
        self.url = reverse("playstyle_compass:delete_list_comment", args=[self.comment.id])

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_deletes_comment_if_owner(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})
        self.assertFalse(ListComment.objects.filter(id=self.comment.id).exists())

    def test_does_not_delete_if_not_owner(self):
        self.client.login(username="otheruser", password="password")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ListComment.objects.filter(id=self.comment.id).exists())

    def test_rejects_get_request(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False})


class EditListCommentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.userprofile.profile_name = "testuser"
        self.user.userprofile.save()
        self.list = GameList.objects.create(
            title="Test List", owner=self.user, is_public=True
        )

        self.comment = ListComment.objects.create(
            game_list=self.list,
            user=self.user,
            text="Original comment",
            created_at=now(),
        )

        self.url = reverse("playstyle_compass:edit_list_comment", args=[self.comment.id])

    def test_can_edit_comment(self):
        self.client.login(username="testuser", password="password")

        data = {"text": "Updated comment"}
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 200)
        expected_created_at = localtime(self.comment.created_at).strftime("%d/%m/%Y - %H:%M")
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {
                "success": True,
                "message": "Comment updated successfully.",
                "comment_text": "Updated comment",
                "created_at": expected_created_at,
                "profile_url": reverse("users:view_profile", kwargs={"profile_name": "testuser"}),
                "profile_name": "testuser",
                "delete_url": reverse("playstyle_compass:delete_list_comment", args=[self.comment.id]),
                "edit_url": self.url,
            },
        )

    def test_cannot_edit_if_text_is_empty(self):
        self.client.login(username="testuser", password="password")

        data = {"text": " "}
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json().get("errors", {}))
        self.assertIn("This field is required.", response.json()["errors"]["text"])

    def test_cannot_edit_after_time_limit(self):
        self.client.login(username="testuser", password="password")

        self.comment.created_at = now() - timedelta(minutes=11)
        self.comment.save()

        response = self.client.post(self.url, {"text": "Late edit"}, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn("You can no longer edit this comment", response.json()["error"])

    def test_get_returns_edit_form(self):
        self.client.login(username="testuser", password="password")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.json())
        self.assertIn("Original comment", response.json()["form"])

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, {"text": "Hello"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class PostListCommentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.userprofile.profile_name = "testuser"
        self.user.userprofile.save()

        self.game_list = GameList.objects.create(
            owner=self.user,
            title="Public List",
            is_public=True
        )

        self.url = reverse("playstyle_compass:post_list_comment", args=[self.game_list.id])

    def test_can_post_comment(self):
        self.client.login(username="testuser", password="password")

        response = self.client.post(self.url, {"text": "This is a test comment"}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["comment_text"], "This is a test comment")
        self.assertEqual(data["profile_name"], "testuser")
        self.assertIn("/en/users/view_profile/testuser/", data["profile_url"])
        self.assertIn("/en/delete-list-comment/", data["delete_url"])
        self.assertIn("/en/edit-comment/", data["edit_url"])
        self.assertIn("created_at", data)

        # Verify the comment was saved in the database
        self.assertTrue(ListComment.objects.filter(user=self.user, game_list=self.game_list).exists())

    def test_cannot_post_empty_comment(self):
        self.client.login(username="testuser", password="password")

        response = self.client.post(self.url, {"text": ""}, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Comment text is required")

        self.assertFalse(ListComment.objects.exists())

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, {"text": "Hello"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_rejects_get_requests(self):
        self.client.login(username="testuser", password="password")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Invalid method")


class LikeGameListCommentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")

        self.game_list = GameList.objects.create(
            owner=self.other_user,
            title="List with Comments",
            is_public=True,
        )

        self.comment = ListComment.objects.create(
            game_list=self.game_list,
            user=self.other_user,
            text="A thoughtful comment"
        )

        self.url = reverse("playstyle_compass:like_list_comment", args=[self.comment.id])

    def test_can_like_comment(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["liked"])
        self.assertEqual(data["like_count"], 1)
        self.assertEqual(data["comment_id"], self.comment.id)

        self.assertIn(self.user, self.comment.liked_by.all())

    def test_can_unlike_comment(self):
        self.comment.liked_by.add(self.user)
        self.client.login(username="testuser", password="password")

        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertFalse(data["liked"])
        self.assertEqual(data["like_count"], 0)
        self.assertEqual(data["comment_id"], self.comment.id)

        self.assertNotIn(self.user, self.comment.liked_by.all())

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class ToggleFavoriteGameListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")

        self.game_list = GameList.objects.create(
            title="Interesting List",
            owner=self.other_user,
            is_public=True,
        )

        self.url = reverse("playstyle_compass:toggle_favorite_game_list", args=[self.game_list.id])

    def test_can_favorite_list(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["favorited"], True)
        self.assertIn(self.user, self.game_list.favorites.all())

    def test_can_unfavorite_list(self):
        self.game_list.favorites.add(self.user)

        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["favorited"], False)
        self.assertNotIn(self.user, self.game_list.favorites.all())

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class FavoriteGameListsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.userprofile.profile_name = "testuser"
        self.user.userprofile.save()

        self.other_user = User.objects.create_user(username="otheruser", password="password")
        self.other_user.userprofile.profile_name = "otheruser"
        self.other_user.userprofile.save()

        self.list1 = GameList.objects.create(
            owner=self.other_user, title="Alpha", game_guids=["1"], is_public=True
        )
        self.list2 = GameList.objects.create(
            owner=self.other_user, title="Bravo", game_guids=["1", "2"], is_public=True
        )
        self.list3 = GameList.objects.create(
            owner=self.user, title="Charlie", game_guids=[], is_public=True
        )

        self.list1.favorites.add(self.user)
        self.list2.favorites.add(self.user)
        self.list3.favorites.add(self.user)

        self.own_url = reverse("playstyle_compass:favorite_game_lists", args=[self.user.id])
        self.other_url = reverse("playstyle_compass:favorite_game_lists", args=[self.other_user.id])

    def test_can_view_own_favorites(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.own_url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha")
        self.assertContains(response, "Bravo")
        self.assertContains(response, "Charlie")
        self.assertFalse(response.context["other_user"])
        self.assertEqual(response.context["viewing_user"], "testuser")

    def test_can_view_another_users_favorites(self):
        self.list1.favorites.add(self.other_user)
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.other_url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha")
        self.assertTrue(response.context["other_user"])
        self.assertEqual(response.context["viewing_user"], "otheruser")

    def test_sorts_by_title_ascending(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.own_url + "?sort_by=title&order=asc", secure=True)

        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertEqual([g.title for g in game_lists], ["Alpha", "Bravo", "Charlie"])

    def test_sorts_by_total_games_descending(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.own_url + "?sort_by=total_games&order=desc", secure=True)

        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertEqual([g.title for g in game_lists], ["Bravo", "Alpha", "Charlie"])

    def test_invalid_sort_fallback(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.own_url + "?sort_by=unknown&order=desc", secure=True)

        self.assertEqual(response.status_code, 200)
        game_lists = response.context["game_lists"]
        self.assertEqual(len(game_lists), 3)

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.own_url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class PopularGamesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("playstyle_compass:popular_games")

    def test_can_view_popular_games(self):
        self.client.login(username="testuser", password="password")

        game1 = Game.objects.create(title="Popular Game 1", guid="123", is_popular=True)
        game2 = Game.objects.create(title="Popular Game 2", guid="3231", is_popular=True)
        game3 = Game.objects.create(title="Not Popular", guid="12343", is_popular=False)

        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/popular_games.html")
        self.assertIn("games", response.context)
        self.assertEqual(list(response.context["games"]), [game1, game2])
        self.assertEqual(response.context["pagination"], True)


class CreatePollViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("playstyle_compass:create_poll")

    def test_can_create_poll(self):
        self.client.login(username="testuser", password="password")
        options_list = ["RPG", "Action", "Strategy"]
        data = {
            "title": "Favorite Genre?",
            "description": "Choose your favorite genre.",
            "options": options_list,
            "duration": 3,
            "is_public": True,
        }

        response = self.client.post(self.url, {
            "title": data["title"],
            "options": data["options"],
            "description": data["description"],
            "duration": data["duration"],
            "is_public": data["is_public"],
        }, secure=True)

        self.assertEqual(response.status_code, 302)

        poll = Poll.objects.first()
        self.assertIsNotNone(poll)
        self.assertEqual(poll.title, data["title"])
        options = PollOption.objects.filter(poll=poll).values_list("text", flat=True)
        self.assertCountEqual(options, data["options"])
        self.assertEqual(poll.description, data["description"])
        self.assertEqual(poll.duration, timedelta(days=data["duration"]))
        self.assertEqual(poll.is_public, data["is_public"])
        self.assertEqual(poll.created_by, self.user)

    def test_does_not_create_with_empty_fields(self):
        self.client.login(username="testuser", password="password")

        response = self.client.post(self.url, {
            "question": "",
            "options": ["", "   ", "\n"],
        }, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/create_poll.html")
        self.assertContains(response, "This field is required")

        self.assertEqual(Poll.objects.count(), 0)
        self.assertEqual(PollOption.objects.count(), 0)

    def test_shows_create_poll_form(self):
        self.client.login(username="testuser", password="password")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/create_poll.html")
        self.assertIn("form", response.context)

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views"])
    sys.exit(bool(failures))
