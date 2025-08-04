from ..base import *


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


class GameDealViewTest(TestCase):
    def setUp(self):
        self.deal = Deal.objects.create(
            deal_id="deal123",
            game_name="Test Game",
            sale_price=9.99,
            retail_price=19.99,
            thumb_url="thumb.jpg",
            store_name="Steam",
            store_icon_url="steam_icon.png",
        )
        self.url = reverse("playstyle_compass:game_deal", args=[self.deal.deal_id])

    def test_page_loads(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "deals/game_deal.html")
        self.assertEqual(response.context["deal"], self.deal)
        self.assertEqual(response.context["page_title"], "Deal Details :: PlayStyle Compass")

    def test_deal_not_found(self):
        bad_url = reverse("playstyle_compass:game_deal", args=["invalid_id"])
        response = self.client.get(bad_url, secure=True)
        self.assertEqual(response.status_code, 404)


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


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_games"])
    sys.exit(bool(failures))
