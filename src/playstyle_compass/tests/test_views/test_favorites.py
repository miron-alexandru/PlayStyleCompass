from ..base import *


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


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_favorites"])
    sys.exit(bool(failures))
