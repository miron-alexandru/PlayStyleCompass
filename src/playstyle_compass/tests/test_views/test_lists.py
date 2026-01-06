from ..base import *


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
