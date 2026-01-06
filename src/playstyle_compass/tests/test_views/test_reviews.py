from ..base import *
from django.utils.translation import gettext_lazy as _

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


class GetGameReviewsViewTest(TestCase):
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


class GameReviewsViewTest(TestCase):
    def setUp(self):
        self.url = reverse("playstyle_compass:game_reviews")
        self.user = User.objects.create_user(username="user", password="pass")

        self.game = Game.objects.create(guid="33421", title="Game 1")

        self.r1 = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="User A",
            review_deck="Deck A",
            review_description="Description A",
            score=4,
            likes=3,
            dislikes=1,
            liked_by="1,2",
            disliked_by="3",
            date_added=now() - timedelta(days=3),
        )

        self.r2 = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="User B",
            review_deck="Deck B",
            review_description="Description B",
            score=2,
            likes=8,
            dislikes=0,
            liked_by="1,2,3,4",
            disliked_by="",
            date_added=now() - timedelta(days=1),
        )

        self.r3 = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="User C",
            review_deck="Deck C",
            review_description="Description C",
            score=5,
            likes=1,
            dislikes=2,
            liked_by="5",
            disliked_by="6,7",
            date_added=now(),
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_page_loads(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/game_reviews.html")
        self.assertIn("reviews", response.context)
        self.assertTrue(response.context["pagination"])
        self.assertEqual(response.context["sort_order"], "date_desc")

    def test_sort_date_asc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=date_asc", secure=True)
        reviews = list(response.context["reviews"])
        dates = [r.date_added for r in reviews]
        self.assertEqual(dates, sorted(dates))

    def test_sort_date_desc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=date_desc", secure=True)
        reviews = list(response.context["reviews"])
        dates = [r.date_added for r in reviews]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_sort_score_asc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=score_asc", secure=True)
        scores = [r.score for r in response.context["reviews"]]
        self.assertEqual(scores, sorted(scores))

    def test_sort_score_desc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=score_desc", secure=True)
        scores = [r.score for r in response.context["reviews"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_sort_likes_asc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=likes_asc", secure=True)
        likes = [r.likes for r in response.context["reviews"]]
        self.assertEqual(likes, sorted(likes))

    def test_sort_likes_desc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=likes_desc", secure=True)
        likes = [r.likes for r in response.context["reviews"]]
        self.assertEqual(likes, sorted(likes, reverse=True))


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


class SingleReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
        )

        self.review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="Test Reviewer",
            review_deck="Brief summary of review",
            review_description="Detailed review content goes here.",
            score=4,
            likes=0,
            dislikes=0,
            liked_by="",
            disliked_by="",
        )

        self.url = reverse("playstyle_compass:single_review", args=[self.review.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_review_page(self):
        self.client.login(username="user", password="pass")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/single_review.html")
        self.assertEqual(response.context["review"], self.review)
        self.assertIn("Game Review :: PlayStyle Compass", response.context["page_title"])

    def test_404_for_invalid_review_id(self):
        self.client.login(username="user", password="pass")
        invalid_url = reverse("playstyle_compass:single_review", args=[9999])
        response = self.client.get(invalid_url, secure=True)
        self.assertEqual(response.status_code, 404)


class ShareReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.friend1 = User.objects.create_user(username="friend1", password="pass")
        self.friend2 = User.objects.create_user(username="friend2", password="pass")

        self.game = Game.objects.create(
            guid="123432",
            title="Test Game",
        )

        self.review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="Reviewer Name",
            review_deck="Short summary",
            review_description="Detailed review text",
            score=4,
            likes=0,
            dislikes=0,
            liked_by="",
            disliked_by="",
        )

        self.url = reverse("playstyle_compass:share_review", args=[self.review.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    @patch("playstyle_compass.views.get_friend_list")
    def test_get_share_review_page(self, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]

        self.client.login(username="user", password="pass")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/share_review.html")
        self.assertEqual(response.context["review"], self.review)
        self.assertEqual(response.context["review_id"], self.review.id)
        self.assertIn(self.friend1, response.context["user_friends"])
        self.assertIn(self.friend2, response.context["user_friends"])

    @patch("playstyle_compass.views.get_friend_list")
    @patch("playstyle_compass.views.create_notification")
    def test_post_share_review_with_friends(self, mock_create_notification, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]

        self.client.login(username="user", password="pass")
        data = {
            "shared_with": [str(self.friend1.id), str(self.friend2.id)]
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        expected_redirect = reverse("playstyle_compass:single_review", args=[self.review.id])
        self.assertEqual(response.url, expected_redirect)

        self.assertTrue(SharedReview.objects.filter(sender=self.user, recipient=self.friend1, review=self.review).exists())
        self.assertTrue(SharedReview.objects.filter(sender=self.user, recipient=self.friend2, review=self.review).exists())

        self.assertEqual(mock_create_notification.call_count, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Review shared successfully." in str(m) for m in messages))

    @patch("playstyle_compass.views.get_friend_list")
    @patch("playstyle_compass.views.create_notification")
    def test_post_does_not_share_with_self(self, mock_create_notification, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2, self.user]

        self.client.login(username="user", password="pass")
        data = {
            "shared_with": [str(self.user.id), str(self.friend1.id)]
        }
        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(SharedReview.objects.filter(sender=self.user, recipient=self.friend1, review=self.review).exists())
        self.assertFalse(SharedReview.objects.filter(sender=self.user, recipient=self.user, review=self.review).exists())

        self.assertEqual(mock_create_notification.call_count, 1)

    @patch("playstyle_compass.views.get_friend_list")
    def test_post_invalid_friend_id_raises_404(self, mock_get_friend_list):
        mock_get_friend_list.return_value = [self.friend1, self.friend2]

        self.client.login(username="user", password="pass")
        data = {
            "shared_with": ["999999"]
        }
        response = self.client.post(self.url, data, secure=True)
        self.assertEqual(response.status_code, 404)


class SharedReviewsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.friend = User.objects.create_user(username="friend", password="pass")

        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
        )

        self.review = Review.objects.create(
            game=self.game,
            user=self.friend,
            reviewers="Reviewer Name",
            review_deck="Short summary",
            review_description="Detailed review text",
            score=4,
            likes=0,
            dislikes=0,
        )

        self.shared_received = SharedReview.objects.create(
            sender=self.friend,
            recipient=self.user,
            review=self.review,
        )

        self.shared_sent = SharedReview.objects.create(
            sender=self.user,
            recipient=self.friend,
            review=self.review,
        )

        self.url = reverse("playstyle_compass:shared_reviews")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_view_received_shared_reviews(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/shared_reviews.html")
        self.assertEqual(response.context["view_type"], "received")
        reviews = response.context["reviews"]
        self.assertIn(self.shared_received, reviews)
        self.assertNotIn(self.shared_sent, reviews)

    def test_view_shared_shared_reviews(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?view=shared", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/shared_reviews.html")
        self.assertEqual(response.context["view_type"], "shared")
        reviews = response.context["reviews"]
        self.assertIn(self.shared_sent, reviews)
        self.assertNotIn(self.shared_received, reviews)
