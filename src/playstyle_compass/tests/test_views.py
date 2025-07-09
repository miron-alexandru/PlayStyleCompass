import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()


import random

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from playstyle_compass.models import *
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
            reverse("playstyle_compass:gaming_preferences"), follow=True
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
            reverse("playstyle_compass:gaming_preferences"), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertContains(response, "Log in")


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views"])
    sys.exit(bool(failures))
