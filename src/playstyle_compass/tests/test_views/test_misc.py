from ..base import *
from django.utils.translation import gettext_lazy as _


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


class DealsListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("playstyle_compass:deals_list")
        now = timezone.now()

        self.deal1 = Deal.objects.create(
            deal_id="d1",
            game_name="Alpha",
            sale_price=5.99,
            retail_price=19.99,
            thumb_url="alpha.jpg",
            store_name="Steam",
            store_icon_url="steam_icon.png",
        )
        self.deal2 = Deal.objects.create(
            deal_id="d2",
            game_name="Bravo",
            sale_price=2.99,
            retail_price=14.99,
            thumb_url="bravo.jpg",
            store_name="Epic",
            store_icon_url="epic_icon.png",
        )
        self.deal3 = Deal.objects.create(
            deal_id="d3",
            game_name="Charlie",
            sale_price=8.99,
            retail_price=29.99,
            thumb_url="charlie.jpg",
            store_name="Steam",
            store_icon_url="steam_icon.png",
        )

    def test_page_loads(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "deals/deals.html")

    def test_sort_game_name_asc(self):
        response = self.client.get(self.url + "?sort_order=game_name_asc", secure=True)
        deals = list(response.context["deals"])
        names = [d.game_name for d in deals]
        self.assertEqual(names, sorted(names))

    def test_sort_game_name_desc(self):
        response = self.client.get(self.url + "?sort_order=game_name_desc", secure=True)
        deals = list(response.context["deals"])
        names = [d.game_name for d in deals]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_sort_sale_price_asc(self):
        response = self.client.get(self.url + "?sort_order=sale_asc", secure=True)
        deals = list(response.context["deals"])
        prices = [d.sale_price for d in deals]
        self.assertEqual(prices, sorted(prices))

    def test_sort_sale_price_desc(self):
        response = self.client.get(self.url + "?sort_order=sale_desc", secure=True)
        deals = list(response.context["deals"])
        prices = [d.sale_price for d in deals]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_filter_by_store(self):
        response = self.client.get(self.url + "?store_name=Steam", secure=True)
        deals = response.context["deals"]
        for d in deals:
            self.assertEqual(d.store_name, "Steam")
        self.assertEqual(response.context["current_store_name"], "Steam")

    def test_filter_and_sort(self):
        response = self.client.get(self.url + "?store_name=Steam&sort_order=sale_asc", secure=True)
        deals = response.context["deals"]
        prices = [d.sale_price for d in deals]
        self.assertEqual(prices, sorted(prices))
        for d in deals:
            self.assertEqual(d.store_name, "Steam")

    def test_available_stores_context(self):
        response = self.client.get(self.url, secure=True)
        stores = list(response.context["available_stores"])
        self.assertIn("Steam", stores)
        self.assertIn("Epic", stores)


class ShareDealViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.friend1 = User.objects.create_user(username="friend1", password="pass")
        self.friend2 = User.objects.create_user(username="friend2", password="pass")

        self.deal = Deal.objects.create(
            deal_id="3324123",
            game_name="Test Game",
            sale_price=5.99,
            retail_price=9.99,
            thumb_url="thumb.jpg",
            store_name="Steam",
            store_icon_url="steam_icon.png",
        )

        self.url = reverse("playstyle_compass:share_deal", args=[self.deal.deal_id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    @patch("playstyle_compass.views.get_friend_list")
    def test_get_share_deal_page(self, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]
        self.client.login(username="user", password="pass")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "deals/share_deal.html")
        self.assertEqual(response.context["deal"], self.deal)
        self.assertEqual(response.context["deal_id"], str(self.deal.deal_id))
        self.assertIn(self.friend1, response.context["user_friends"])
        self.assertIn(self.friend2, response.context["user_friends"])

    @patch("playstyle_compass.views.get_friend_list")
    def test_post_share_deal_with_friends(self, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]
        self.client.login(username="user", password="pass")

        data = {
            "shared_with": [str(self.friend1.id), str(self.friend2.id)]
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        expected_redirect = reverse("playstyle_compass:game_deal", args=[self.deal.deal_id])
        self.assertEqual(response.url, expected_redirect)

        self.assertTrue(SharedDeal.objects.filter(sender=self.user, recipient=self.friend1, deal=self.deal).exists())
        self.assertTrue(SharedDeal.objects.filter(sender=self.user, recipient=self.friend2, deal=self.deal).exists())

    @patch("playstyle_compass.views.get_friend_list")
    def test_post_does_not_share_with_self(self, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]
        self.client.login(username="user", password="pass")

        data = {
            "shared_with": [str(self.user.id), str(self.friend1.id)]
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(SharedDeal.objects.filter(sender=self.user, recipient=self.friend1, deal=self.deal).exists())
        self.assertFalse(SharedDeal.objects.filter(sender=self.user, recipient=self.user, deal=self.deal).exists())

    @patch("playstyle_compass.views.get_friend_list")
    def test_post_invalid_friend_id_raises_404(self, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]
        self.client.login(username="user", password="pass")

        data = {
            "shared_with": ["999999"]
        }
        response = self.client.post(self.url, data, secure=True)
        self.assertEqual(response.status_code, 404)


class SharedDealsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.friend = User.objects.create_user(username="friend", password="pass")
        self.deal = Deal.objects.create(
            deal_id="12345",
            game_name="Sample Game",
            sale_price=10.0,
            retail_price=20.0,
            thumb_url="thumb.jpg",
            store_name="Steam",
            store_icon_url="steam_icon.png",
        )
        self.url = reverse("playstyle_compass:shared_deals")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_default_view_receives_deals(self):
        SharedDeal.objects.create(sender=self.friend, recipient=self.user, deal=self.deal)
        self.client.login(username="user", password="pass")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["view_type"], "received")
        deals = response.context["deals"]
        self.assertTrue(all(d.recipient == self.user for d in deals))
        self.assertIn("Shared Deals :: PlayStyle Compass", response.context["page_title"])

    def test_view_shared_deals_sent(self):
        SharedDeal.objects.create(sender=self.user, recipient=self.friend, deal=self.deal)
        self.client.login(username="user", password="pass")

        response = self.client.get(f"{self.url}?view=shared", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["view_type"], "shared")
        deals = response.context["deals"]
        self.assertTrue(all(d.sender == self.user for d in deals))
        self.assertIn("Shared Deals :: PlayStyle Compass", response.context["page_title"])

    def test_no_deals_for_user(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["deals"]), 0)


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




if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_misc"])
    sys.exit(bool(failures))