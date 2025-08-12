from .base import *
import json
import ast


class QuizViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="u1@example.com", password="pass1234"
        )
        self.url = reverse("users:gaming_quiz")

    @patch("users.views.check_quiz_time", return_value=None)
    @patch("users.views.get_quiz_questions")
    def test_get_quiz_view_authenticated(self, mock_get_questions, mock_check_time):
        mock_get_questions.return_value = [
            MagicMock(
                id=1,
                question_text="Question 1",
                option1="A",
                option2="B",
                option3="C",
                option4="D",
            )
        ]
        self.client.login(username="user1", password="pass1234")

        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general/quiz_template.html")
        self.assertIsInstance(response.context["form"], QuizForm)
        self.assertEqual(response.context["questions"], mock_get_questions.return_value)

    @patch("users.views.check_quiz_time", return_value="5 hours")
    def test_quiz_time_limit_redirects(self, mock_check_time):
        self.client.login(username="user1", password="pass1234")

        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("playstyle_compass:index"), response.url)

    @patch("users.views.check_quiz_time", return_value=None)
    @patch("users.views.get_quiz_questions")
    @patch("users.views.save_quiz_responses")
    @patch("users.views.QuizRecommendations")
    def test_post_valid_quiz(
        self,
        mock_quiz_recs,
        mock_save_responses,
        mock_get_questions,
        mock_check_time,
    ):
        question = MagicMock(
            id=1,
            question_text="Question 1",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
        )
        mock_get_questions.return_value = [question]
        self.client.login(username="user1", password="pass1234")

        data = {f"question_{question.id}": "option1"}

        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("playstyle_compass:index"), response.url)
        self.user.userprofile.refresh_from_db()
        self.assertTrue(self.user.userprofile.quiz_taken)
        self.assertIsNotNone(self.user.userprofile.quiz_taken_date)
        mock_save_responses.assert_called_once()
        mock_quiz_recs.assert_called_once()

    @patch("users.views.check_quiz_time", return_value=None)
    @patch("users.views.get_quiz_questions")
    def test_post_invalid_quiz_form(self, mock_get_questions, mock_check_time):
        question = MagicMock(
            id=1,
            question_text="Question 1",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
        )
        mock_get_questions.return_value = [question]
        self.client.login(username="user1", password="pass1234")

        data = {}

        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general/quiz_template.html")
        self.assertTrue(response.context["form"].errors)

    def test_unauthenticated_access(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class QuizRecommendationsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.url = reverse("users:quiz_recommendations")
        self.preferences = self.user.userpreferences

    def login(self):
        self.client.login(username="testuser", password="pass")

    def test_requires_login(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_no_recommendations(self):
        self.login()
        self.preferences.quiz_recommendations = "[]"
        self.preferences.save()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quiz Recommendations")
        self.assertQuerySetEqual(response.context["games"], [])

    def test_with_recommendations(self):
        self.login()
        game1 = Game.objects.create(guid="1234", title="Game 1")
        game2 = Game.objects.create(guid="1241", title="Game 2")
        self.preferences.quiz_recommendations = str([game1.guid, game2.guid])
        self.preferences.save()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        games = list(response.context["games"])
        self.assertIn(game1, games)
        self.assertIn(game2, games)

    def test_pagination(self):
        self.login()
        guids = []
        for i in range(15):
            game = Game.objects.create(guid=f"{i}", title=f"Game {i}")
            guids.append(game.guid)
        self.preferences.quiz_recommendations = str(guids)
        self.preferences.save()
        response = self.client.get(self.url + "?page=2", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("games" in response.context)


class ContactViewTest(TestCase):
    def setUp(self):
        self.url = reverse("users:contact")

    def test_get_contact_form(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general/contact.html")
        self.assertIsInstance(response.context["form"], ContactForm)

    @patch("users.views.send_mail")
    @patch("users.views.ContactForm.save")
    def test_post_valid_form(self, mock_save, mock_send_mail):
        mock_save.return_value = type(
            "ContactMessage",
            (),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test Subject",
                "message": "Test message",
                "formatted_timestamp": lambda self=None: "2025-01-01 10:00",
            },
        )()
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message",
        }

        response = self.client.post(self.url, form_data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:contact_success"))
        mock_save.assert_called_once()
        mock_send_mail.assert_called_once()

    def test_post_invalid_form(self):
        form_data = {"name": "", "email": "invalid-email", "subject": "", "message": ""}
        response = self.client.post(self.url, form_data, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general/contact.html")
        self.assertTrue(response.context["form"].errors)


class ContactSuccessViewTest(TestCase):
    def setUp(self):
        self.url = reverse("users:contact_success")

    def test_get_contact_success(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_actions/change_succeeded.html")
        self.assertIn("page_title", response.context)
        self.assertIn("response", response.context)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("successfully submitted" in str(m) for m in messages))


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_misc"])
    sys.exit(bool(failures))

