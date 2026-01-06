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
