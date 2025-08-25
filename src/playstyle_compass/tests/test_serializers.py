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
from rest_framework.utils.serializer_helpers import ReturnDict
from playstyle_compass.serializers import (
    DynamicFieldsModelSerializer,
    GameSerializer,
    GameReviewSerializer,
)
from playstyle_compass.models import Game, Review, Franchise
from django.contrib.auth import get_user_model


User = get_user_model()


class DynamicFieldsModelSerializerTest(TestCase):
    def setUp(self):
        self.franchise = Franchise.objects.create(title="Franchise A", games="1234")
        self.game = Game.objects.create(
            guid="1234",
            title="Test Game",
            description="Test description",
            genres="Action",
            platforms="PC",
            themes="Adventure",
            image="image.png",
            videos="trailer.mp4",
            concepts="Concept A",
        )
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.review = Review.objects.create(
            game=self.game,
            user=self.user,
            reviewers="IGN",
            review_deck="Great deck",
            review_description="Good game",
            score=4,
        )

    def test_all_game_fields(self):
        serializer = GameSerializer(instance=self.game)
        data = serializer.data
        self.assertIsInstance(data, ReturnDict)
        for field in [f.name for f in Game._meta.fields]:
            self.assertIn(field, data)

    def test_select_fields(self):
        serializer = GameSerializer(instance=self.game, fields=["id", "title"])
        self.assertEqual(set(serializer.data.keys()), {"id", "title"})

    def test_fields_read_only(self):
        serializer = GameSerializer()
        for field in serializer.fields.values():
            self.assertTrue(field.read_only)

    def test_review_serializer_excludes_user(self):
        serializer = GameReviewSerializer(instance=self.review)
        data = serializer.data
        self.assertNotIn("user", data)
        self.assertIn("review_description", data)
        self.assertIn("score", data)

    def test_review_dynamic_fields(self):
        serializer = GameReviewSerializer(instance=self.review, fields=["id", "review_description"])
        self.assertEqual(set(serializer.data.keys()), {"id", "review_description"})


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_serializers"])
    sys.exit(bool(failures))