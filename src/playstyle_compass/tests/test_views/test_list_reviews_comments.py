from ..base import *


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



if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_views.test_list_reviews_comments"])
    sys.exit(bool(failures))
