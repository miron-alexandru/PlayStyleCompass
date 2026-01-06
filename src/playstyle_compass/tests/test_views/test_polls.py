from ..base import *


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



class VoteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="voter", password="password")
        self.poll = Poll.objects.create(
            title="Best Genre?",
            description="Vote for your favorite genre.",
            created_by=self.user,
            duration=timedelta(days=3),
            is_public=True,
        )
        self.option1 = PollOption.objects.create(poll=self.poll, text="RPG")
        self.option2 = PollOption.objects.create(poll=self.poll, text="Action")
        self.url = reverse("playstyle_compass:vote", args=[self.poll.id])

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_can_vote(self):
        self.client.login(username="voter", password="password")

        response = self.client.post(self.url, {
            "option": self.option1.id,
        }, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vote.objects.count(), 1)
        vote = Vote.objects.first()
        self.assertEqual(vote.poll, self.poll)
        self.assertEqual(vote.option, self.option1)
        self.assertEqual(vote.user, self.user)

    def test_cannot_vote_twice(self):
        self.client.login(username="voter", password="password")

        self.client.post(self.url, {"option": self.option1.id}, secure=True)

        response = self.client.post(self.url, {"option": self.option2.id}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vote.objects.count(), 1)

    def test_cannot_vote_if_poll_has_ended(self):
        self.client.login(username="voter", password="password")

        self.poll.created_at = timezone.now() - timedelta(days=5)
        self.poll.save()

        response = self.client.post(self.url, {"option": self.option1.id}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vote.objects.count(), 0)

    def test_invalid_vote_form(self):
        self.client.login(username="voter", password="password")

        response = self.client.post(self.url, {}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vote.objects.count(), 0)


class CommunityPollsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("playstyle_compass:community_polls")

        self.public_poll = Poll.objects.create(
            title="Best Genre?",
            description="Vote for your favorite genre",
            duration=timedelta(days=3),
            is_public=True,
            created_by=self.user,
        )

        self.option1 = PollOption.objects.create(poll=self.public_poll, text="RPG")
        self.option2 = PollOption.objects.create(poll=self.public_poll, text="Action")

        self.private_poll = Poll.objects.create(
            title="Hidden Poll",
            description="This should not appear",
            duration=timedelta(days=2),
            is_public=False,
            created_by=self.user,
        )
        PollOption.objects.create(poll=self.private_poll, text="Hidden Option")

    def test_loads_successfully(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/community_polls.html")

    def test_shows_only_public_polls(self):
        response = self.client.get(self.url, secure=True)
        polls = response.context["polls"]
        self.assertIn(self.public_poll, polls)
        self.assertNotIn(self.private_poll, polls)

    def test_poll_context_has_vote_data(self):
        self.client.login(username="testuser", password="password")
        Vote.objects.create(user=self.user, poll=self.public_poll, option=self.option1)

        response = self.client.get(self.url, secure=True)
        user_votes = response.context["user_votes"]

        self.assertIn(self.public_poll.id, user_votes)
        self.assertEqual(user_votes[self.public_poll.id], self.option1.id)

    def test_context_contains_options_with_percentages(self):
        Vote.objects.create(user=self.user, poll=self.public_poll, option=self.option1)

        response = self.client.get(self.url, secure=True)
        polls_with_data = response.context["polls_with_data"]

        self.assertTrue(polls_with_data)
        poll_data = polls_with_data[0]
        self.assertIn("poll", poll_data)
        self.assertIn("total_votes", poll_data)
        self.assertIn("options_with_percentages", poll_data)

        percentages = poll_data["options_with_percentages"]
        self.assertTrue(all("percentage" in opt for opt in percentages))


class UserPollsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass")
        self.other_user = User.objects.create_user(username="visitor", password="pass")
        self.url = reverse("playstyle_compass:user_polls", args=[self.user.id])

        self.poll = Poll.objects.create(
            title="Favorite Game?",
            description="Vote your top game.",
            created_by=self.user,
            duration=timedelta(days=3),
            is_public=True,
            created_at=timezone.now()
        )
        self.option1 = PollOption.objects.create(poll=self.poll, text="Skyrim")
        self.option2 = PollOption.objects.create(poll=self.poll, text="Witcher 3")

    def test_redirects_if_logged_out(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_loads_for_other_user(self):
        self.client.login(username="visitor", password="pass")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/user_polls.html")

        context = response.context
        self.assertIn("polls_with_data", context)
        self.assertIn("user_votes", context)
        self.assertEqual(context["user_polls"], self.user)
        self.assertFalse(context["is_own_polls"])

    def test_loads_own_polls(self):
        self.client.login(username="owner", password="pass")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.context["user_polls"], self.user)
        self.assertTrue(response.context["is_own_polls"])

    def test_shows_user_vote(self):
        Vote.objects.create(poll=self.poll, option=self.option1, user=self.other_user)
        self.client.login(username="visitor", password="pass")

        response = self.client.get(self.url, secure=True)
        user_votes = response.context["user_votes"]

        self.assertIn(self.poll.id, user_votes)
        self.assertEqual(user_votes[self.poll.id], self.option1.id)

    def test_shows_vote_stats(self):
        self.client.login(username="visitor", password="pass")
        response = self.client.get(self.url, secure=True)
        polls_with_data = response.context["polls_with_data"]

        self.assertEqual(len(polls_with_data), 1)
        self.assertIn("total_votes", polls_with_data[0])
        self.assertIn("options_with_percentages", polls_with_data[0])


class DeletePollTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.poll = Poll.objects.create(
            title="Test Poll",
            description="Desc",
            created_by=self.owner,
            duration=timedelta(days=3),
            is_public=True,
            created_at=timezone.now(),
        )
        self.url = reverse("playstyle_compass:delete_poll", args=[self.poll.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_owner_can_delete(self):
        self.client.login(username="owner", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("playstyle_compass:user_polls", args=[self.owner.id]), response.url)
        self.assertFalse(Poll.objects.filter(id=self.poll.id).exists())

    def test_non_owner_cannot_delete(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("playstyle_compass:user_polls", args=[self.other.id]), response.url)
        self.assertTrue(Poll.objects.filter(id=self.poll.id).exists())

    def test_message_on_success(self):
        self.client.login(username="owner", password="pass")
        response = self.client.post(self.url, secure=True, follow=True)
        messages_list = list(response.context["messages"])
        self.assertTrue(any("deleted successfully" in m.message for m in messages_list))

    def test_message_on_unauthorized(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(self.url, secure=True, follow=True)
        messages_list = list(response.context["messages"])
        self.assertTrue(any("not authorized" in m.message for m in messages_list))


class VotedPollsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="voter", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")

        self.poll1 = Poll.objects.create(
            title="Poll 1",
            description="Desc 1",
            created_by=self.other_user,
            duration=timedelta(days=3),
            is_public=True,
            created_at=timezone.now(),
        )
        self.option1 = PollOption.objects.create(poll=self.poll1, text="Option 1")
        self.option2 = PollOption.objects.create(poll=self.poll1, text="Option 2")

        self.poll2 = Poll.objects.create(
            title="Poll 2",
            description="Desc 2",
            created_by=self.other_user,
            duration=timedelta(days=3),
            is_public=True,
            created_at=timezone.now(),
        )
        self.option3 = PollOption.objects.create(poll=self.poll2, text="Option 3")

        self.url = reverse("playstyle_compass:voted_polls")

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_no_votes_shows_empty(self):
        self.client.login(username="voter", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["polls_with_data"]), 0)
        self.assertEqual(response.context["user_votes"], {})

    def test_votes_show_correct_polls(self):
        Vote.objects.create(user=self.user, poll=self.poll1, option=self.option1)
        Vote.objects.create(user=self.user, poll=self.poll2, option=self.option3)
        self.client.login(username="voter", password="pass")

        response = self.client.get(self.url, secure=True)
        polls_with_data = response.context["polls_with_data"]
        user_votes = response.context["user_votes"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(polls_with_data), 2)
        poll_ids = [data["poll"].id for data in polls_with_data]
        self.assertIn(self.poll1.id, poll_ids)
        self.assertIn(self.poll2.id, poll_ids)

        self.assertIn(self.poll1.id, user_votes)
        self.assertEqual(user_votes[self.poll1.id], self.option1.id)
        self.assertIn(self.poll2.id, user_votes)
        self.assertEqual(user_votes[self.poll2.id], self.option3.id)

    def test_context_contains_page_title(self):
        self.client.login(username="voter", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertIn("page_title", response.context)
        self.assertIn("Voted Polls", response.context["page_title"])


class LikePollTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.poll = Poll.objects.create(
            title="Test Poll",
            description="Desc",
            created_by=self.user,
            duration=timedelta(days=1),
            is_public=True,
        )
        self.url = reverse("playstyle_compass:like_poll", args=[self.poll.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_like_poll(self):
        self.client.login(username="tester", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["liked"])
        self.assertEqual(data["poll_id"], self.poll.id)
        self.assertEqual(data["like_count"], 1)

    def test_unlike_poll(self):
        self.poll.liked_by.add(self.user)
        self.client.login(username="tester", password="pass")
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["liked"])
        self.assertEqual(data["poll_id"], self.poll.id)
        self.assertEqual(data["like_count"], 0)


class PollDetailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.poll = Poll.objects.create(
            title="Test Poll",
            description="Desc",
            created_by=self.user,
            duration=timedelta(days=1),
            is_public=True,
            created_at=timezone.now()
        )
        self.option1 = PollOption.objects.create(poll=self.poll, text="Option 1")
        self.option2 = PollOption.objects.create(poll=self.poll, text="Option 2")
        self.url = reverse("playstyle_compass:poll_detail", args=[self.poll.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_page_loads(self):
        self.client.login(username="tester", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/poll_detail.html")

    def test_context_has_poll_data(self):
        self.client.login(username="tester", password="pass")
        response = self.client.get(self.url, secure=True)
        context = response.context

        self.assertEqual(context["poll"], self.poll)
        self.assertIn("total_votes", context)
        self.assertIn("options_with_percentages", context)
        self.assertIn("user_votes", context)
        self.assertIsInstance(context["user_votes"], dict)
        self.assertNotIn(self.poll.id, context["user_votes"])

    def test_user_vote_in_context(self):
        Vote.objects.create(poll=self.poll, option=self.option1, user=self.user)
        self.client.login(username="tester", password="pass")
        response = self.client.get(self.url, secure=True)
        user_votes = response.context["user_votes"]
        self.assertIn(self.poll.id, user_votes)
        self.assertEqual(user_votes[self.poll.id], self.option1.id)


class SharePollTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass")
        self.friend = User.objects.create_user(username="friend", password="pass")
        self.poll = Poll.objects.create(
            title="Favorite Game?",
            description="A test poll",
            created_by=self.user,
            duration=timedelta(days=1),
            is_public=True,
            created_at=timezone.now()
        )
        self.url = reverse("playstyle_compass:share_poll", args=[self.poll.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    @patch("playstyle_compass.views.get_user_context")
    def test_page_loads(self, mock_context):
        mock_context.return_value = (self.user, None, [self.friend])
        self.client.login(username="owner", password="pass")

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/share_poll.html")
        self.assertEqual(response.context["poll"], self.poll)
        self.assertEqual(response.context["user_friends"], [self.friend])

    def test_post_with_no_users_returns_400(self):
        self.client.login(username="owner", password="pass")
        response = self.client.post(self.url, data={}, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"At least one friend must be selected", response.content)

    @patch("playstyle_compass.views.create_notification")
    def test_poll_sharing_success(self, mock_notify):
        self.client.login(username="owner", password="pass")
        response = self.client.post(
            self.url, data={"shared_with": [str(self.friend.id)]}, secure=True
        )

        self.poll.refresh_from_db()
        self.assertIn(self.friend, self.poll.shared_with.all())
        self.assertIn(str(self.user.id), self.poll.shared_by)
        self.assertIn(str(self.friend.id), self.poll.shared_by[str(self.user.id)])

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("playstyle_compass:poll_detail", args=[self.poll.id]),
            response.url
        )

        mock_notify.assert_called_once()



class SharedPollsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.friend = User.objects.create_user(username="friend", password="pass")

        self.poll1 = Poll.objects.create(
            title="Poll A",
            description="Test poll A",
            created_by=self.friend,
            duration=timedelta(days=2),
            is_public=True,
            created_at=timezone.now() - timedelta(days=1)
        )
        self.poll2 = Poll.objects.create(
            title="Poll B",
            description="Test poll B",
            created_by=self.user,
            duration=timedelta(days=2),
            is_public=True,
            created_at=timezone.now()
        )

        self.poll1.shared_with.add(self.user)
        self.poll1.shared_by = {str(self.friend.id): [str(self.user.id)]}
        self.poll1.save()

        self.poll2.shared_with.add(self.friend)
        self.poll2.shared_by = {str(self.user.id): [str(self.friend.id)]}
        self.poll2.save()

        self.url = reverse("playstyle_compass:shared_polls")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_view_shared_with_me(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/shared_polls.html")

        polls = response.context["polls"]
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0], self.poll1)
        self.assertEqual(response.context["view_type"], "received")
        self.assertTrue(hasattr(polls[0], "shared_by_users"))
        self.assertIn(self.friend, polls[0].shared_by_users)

    def test_view_shared_by_me(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?view=shared", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/shared_polls.html")

        polls = response.context["polls"]
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0], self.poll2)
        self.assertEqual(response.context["view_type"], "shared")

    def test_sorting_by_title(self):
        self.client.login(username="user", password="pass")
        self.poll1.title = "Zebra"
        self.poll1.save()

        response = self.client.get(self.url + "?sort_by=title&order=asc", secure=True)
        polls = response.context["polls"]

        self.assertEqual(polls[0].title, "Zebra")

    def test_sorting_by_created_at(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_by=created_at&order=asc", secure=True)
        polls = response.context["polls"]

        self.assertTrue(polls[0].created_at <= polls[-1].created_at)


class CompletedPollsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.url = reverse("playstyle_compass:completed_polls")

        self.completed_poll = Poll.objects.create(
            title="Finished Poll",
            description="Done",
            created_by=self.user,
            is_public=True,
            duration=timedelta(days=7)
        )
        self.completed_poll.created_at = timezone.now() - timedelta(days=8)
        self.completed_poll.save()

        self.completed_poll_option = PollOption.objects.create(
            poll=self.completed_poll, text="Option A"
        )

        self.active_poll = Poll.objects.create(
            title="Active Poll",
            description="Still running",
            created_by=self.user,
            duration=timedelta(days=10),
            is_public=True,
            created_at=timezone.now()
        )
        PollOption.objects.create(poll=self.active_poll, text="Option B")

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    @patch("playstyle_compass.views.paginate_objects")
    def test_completed_poll_is_listed(self, mock_paginate):
        self.client.login(username="testuser", password="pass")

        mock_paginate.return_value = [self.completed_poll, self.active_poll]

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/completed_polls.html")

        context = response.context
        self.assertIn("polls_with_data", context)
        self.assertEqual(len(context["polls_with_data"]), 1)

        data = context["polls_with_data"][0]
        self.assertEqual(data["poll"], self.completed_poll)
        self.assertIn("total_votes", data)
        self.assertIn("options_with_percentages", data)
        self.assertEqual(context["polls"][0], self.completed_poll)
        self.assertTrue(context["pagination"])

    @patch("playstyle_compass.views.paginate_objects")
    def test_user_vote_shown_if_exists(self, mock_paginate):
        self.client.login(username="testuser", password="pass")

        Vote.objects.create(user=self.user, poll=self.completed_poll, option=self.completed_poll_option)
        mock_paginate.return_value = [self.completed_poll]

        response = self.client.get(self.url, secure=True)
        user_votes = response.context["user_votes"]
        self.assertIn(self.completed_poll.id, user_votes)
        self.assertEqual(user_votes[self.completed_poll.id], self.completed_poll_option.id)
