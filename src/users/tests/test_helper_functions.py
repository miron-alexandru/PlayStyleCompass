import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.conf import settings
from django.test import TestCase
from users.misc.helper_functions import *
from django.contrib.auth.models import User
from django.core.cache import cache
from users.models import FriendList, QuizQuestion, QuizUserResponse
from playstyle_compass.models import Game
from django.utils import timezone
from datetime import timedelta


class AreFriendsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.user3 = User.objects.create_user(username="user3", password="pass")

        self.friend_list1, _ = FriendList.objects.get_or_create(user=self.user1)
        self.friend_list2, _ = FriendList.objects.get_or_create(user=self.user2)
        self.friend_list3, _ = FriendList.objects.get_or_create(user=self.user3)

    def test_users_are_friends(self):
        self.friend_list1.friends.add(self.user2)
        self.friend_list2.friends.add(self.user1)

        self.assertTrue(are_friends(self.user1, self.user2))
        self.assertTrue(are_friends(self.user2, self.user1))

    def test_users_are_not_friends(self):
        self.friend_list1.friends.add(self.user2)

        self.assertFalse(are_friends(self.user1, self.user2))
        self.assertFalse(are_friends(self.user2, self.user1))

    def test_completely_unrelated_users(self):
        self.assertFalse(are_friends(self.user1, self.user3))



class CheckQuizTimeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.profile = self.user.userprofile

    def test_no_quiz(self):
        self.profile.quiz_taken_date = None
        self.profile.save()
        self.assertIsNone(check_quiz_time(self.user))

    def test_old_quiz(self):
        self.profile.quiz_taken_date = timezone.now() - timedelta(days=2)
        self.profile.save()
        self.assertIsNone(check_quiz_time(self.user))

    def test_quiz_hours_minutes_left(self):
        self.profile.quiz_taken_date = timezone.now() - timedelta(hours=10, minutes=30)
        self.profile.save()
        result = check_quiz_time(self.user)
        self.assertIn(result, ["13h:30m", "13h:29m"])

    def test_quiz_one_hour_left(self):
        self.profile.quiz_taken_date = timezone.now() - timedelta(hours=23)
        self.profile.save()
        result = check_quiz_time(self.user)
        self.assertIn(result, ["1h", "59m"])

    def test_quiz_one_minute_left(self):
        self.profile.quiz_taken_date = timezone.now() - timedelta(hours=23, minutes=59)
        self.profile.save()
        result = check_quiz_time(self.user)
        self.assertIn(result, ["1m", None])

    def test_quiz_exact_day(self):
        self.profile.quiz_taken_date = timezone.now() - timedelta(days=1)
        self.profile.save()
        self.assertIsNone(check_quiz_time(self.user))


class QuizRecommendationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")

        self.question = QuizQuestion.objects.create(
            name="survival",
            option1="Yes",
            option2="Maybe",
            option3="Rarely",
            option4="No",
        )

        self.game1 = Game.objects.create(
            guid="1234",
            title="Survival One",
            concepts="survival",
            genres="action",
            themes="horror",
            platforms="pc",
            developers="dev1",
        )
        self.game2 = Game.objects.create(
            guid="12345",
            title="Survival Two",
            concepts="survival",
            genres="action",
            themes="horror",
            platforms="pc",
            developers="dev1",
        )

    def test_scores(self):
        response = QuizUserResponse.objects.create(
            user=self.user,
            question=self.question,
            response_text="Yes",
        )
        rec = QuizRecommendations([response], self.user)
        scores = rec._calculate_concept_recommendations()
        self.assertEqual(scores["survival"], 4)

    def test_get_games(self):
        concept_scores = defaultdict(int, {"survival": 2})
        rec = QuizRecommendations([], self.user)
        games, guids = rec._get_games_for_concepts(concept_scores)
        titles = [g.title for g in games]
        self.assertIn("Survival One", titles)
        self.assertIn("Survival Two", titles)
        self.assertEqual(set(guids), {"1234", "12345"})

    def test_save_prefs(self):
        rec = QuizRecommendations([], self.user)
        rec._save_recommendations_to_preferences(["1234", "12345"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.userpreferences.quiz_recommendations, "['1234', '12345']")

    def test_full_flow(self):
        response = QuizUserResponse.objects.create(
            user=self.user,
            question=self.question,
            response_text="Maybe",
        )
        rec = QuizRecommendations([response], self.user)
        games = rec.get_recommendations()
        titles = [g.title for g in games]
        self.assertTrue(any("Survival" in t for t in titles))
        self.user.refresh_from_db()
        self.assertTrue(len(self.user.userpreferences.quiz_recommendations) > 0)


class GetQuizQuestionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.cache_key = "quiz_qs"

        for i in range(12):
            QuizQuestion.objects.create(
                name=f"q{i}",
                option1="a",
                option2="b",
                option3="c",
                option4="d",
            )

    def test_returns_10(self):
        questions = get_quiz_questions(self.user, self.cache_key)
        self.assertEqual(len(questions), 10)

    def test_cached(self):
        questions = get_quiz_questions(self.user, self.cache_key)
        cached = cache.get(self.cache_key)
        self.assertEqual(len(cached), 10)
        self.assertEqual(questions, cached)

    def test_resets_flag(self):
        self.user.userprofile.quiz_taken = True
        self.user.userprofile.save()
        _ = get_quiz_questions(self.user, self.cache_key)
        self.user.refresh_from_db()
        self.assertFalse(self.user.userprofile.quiz_taken)


class SaveQuizResponsesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")

        self.question = QuizQuestion.objects.create(
            name="q1",
            option1="a",
            option2="b",
            option3="c",
            option4="d",
            option1_en="a_en", option1_ro="a_ro",
            option2_en="b_en", option2_ro="b_ro",
            option3_en="c_en", option3_ro="c_ro",
            option4_en="d_en", option4_ro="d_ro",
        )

        class DummyForm:
            cleaned_data = {}

        self.form = DummyForm()

    def test_valid_response_saved(self):
        self.form.cleaned_data = {f"question_{self.question.id}": "option1"}
        save_quiz_responses(self.user, [self.question], self.form)
        response = QuizUserResponse.objects.get(user=self.user, question=self.question)
        self.assertEqual(response.response_text_en, "a_en")
        self.assertEqual(response.response_text_ro, "a_ro")

    def test_invalid_option_raises(self):
        self.form.cleaned_data = {f"question_{self.question.id}": "invalid"}
        with self.assertRaises(ValidationError):
            save_quiz_responses(self.user, [self.question], self.form)

    def test_missing_translation_raises(self):
        q2 = QuizQuestion.objects.create(
            name="q2",
            option1="x",
            option2="y",
            option3="z",
        )
        self.form.cleaned_data = {f"question_{q2.id}": "option1"}
        with self.assertRaises(ValidationError):
            save_quiz_responses(self.user, [q2], self.form)

if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_helper_functions"])
    sys.exit(bool(failures))