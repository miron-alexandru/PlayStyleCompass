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
from users.models import FriendList
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




if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_helper_functions"])
    sys.exit(bool(failures))