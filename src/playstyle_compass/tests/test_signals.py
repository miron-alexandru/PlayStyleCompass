import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.conf import settings
from unittest.mock import patch
from django.test import TestCase
from playstyle_compass.models import Game

class GameSignalTest(TestCase):
    @patch.object(Game, "update_score")
    def test_update_score_called_on_create(self, mock_update):
        game = Game.objects.create(
            guid="abcd",
            title="Test",
            description="desc",
            genres="Action",
            platforms="PC",
            themes="Theme",
            image="img.png",
            videos="vid.mp4",
            concepts="Concept"
        )
        mock_update.assert_called_once()


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_signals"])
    sys.exit(bool(failures))