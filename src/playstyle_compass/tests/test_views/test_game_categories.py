from ..base import *


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


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_game_categories"])
    sys.exit(bool(failures))