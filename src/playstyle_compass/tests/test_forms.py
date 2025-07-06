import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()


from django.contrib.auth import get_user_model
from django.test import TestCase
from playstyle_compass.models import *
from playstyle_compass.forms import *
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class ReviewFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "review_deck": "Great game!",
            "review_description": "Loved the gameplay and story.",
            "score": 4,
        }

    def test_form_valid_with_valid_data(self):
        form = ReviewForm(data=self.valid_data)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_missing_fields(self):
        form = ReviewForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("review_deck", form.errors)
        self.assertIn("review_description", form.errors)
        self.assertIn("score", form.errors)

    def test_form_score_field_validation(self):
        data = self.valid_data.copy()
        data["score"] = "invalid"
        form = ReviewForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("score", form.errors)

    def test_labels(self):
        form = ReviewForm()
        self.assertEqual(form.fields["review_deck"].label, _("Review Title"))
        self.assertEqual(form.fields["review_description"].label, _("Review"))
        self.assertEqual(form.fields["score"].label, _("Your Rating"))

    def test_widgets_attributes(self):
        form = ReviewForm()
        review_deck_attrs = form.fields["review_deck"].widget.attrs
        self.assertIn("placeholder", review_deck_attrs)
        self.assertEqual(
            review_deck_attrs["placeholder"],
            _("Enter a brief title for your review..."),
        )
        self.assertEqual(review_deck_attrs.get("autofocus"), "autofocus")

        review_description_attrs = form.fields["review_description"].widget.attrs
        self.assertIn("placeholder", review_description_attrs)
        self.assertEqual(
            review_description_attrs["placeholder"],
            _(
                "Share your detailed review of the game, including your thoughts on gameplay, graphics, storyline, and overall experience..."
            ),
        )


class GameListFormTest(TestCase):
    def setUp(self):
        self.game1 = Game.objects.create(
            guid="4123",
            title="The Witcher",
            description="Description one",
            overview="Overview one",
            genres="Action",
            platforms="PC",
            themes="Adventure",
            image="http://example.com/image1.jpg",
            release_date="2025-01-01",
        )
        self.game2 = Game.objects.create(
            guid="5132",
            title="FIFA",
            description="Description two",
            overview="Overview two",
            genres="RPG",
            platforms="Xbox",
            themes="Fantasy",
            image="http://example.com/image2.jpg",
            release_date="2025-02-01",
        )

        self.owner = User.objects.create_user(username="owner", password="testpass")

        self.valid_data = {
            "owner": self.owner,
            "title": "My Favorite Games",
            "description": "A list of my top picks.",
            "games": [self.game1.id, self.game2.id],
            "additional_games": "ExtraGame1, ExtraGame2",
            "is_public": True,
        }

    def test_form_valid_with_valid_data(self):
        form = GameListForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_title(self):
        invalid_data = self.valid_data.copy()
        invalid_data["title"] = ""
        form = GameListForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_invalid_without_games(self):
        invalid_data = self.valid_data.copy()
        invalid_data["games"] = []
        form = GameListForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("games", form.errors)

    def test_clean_additional_games_strips_whitespace(self):
        data = self.valid_data.copy()
        data["additional_games"] = "  GameA , GameB  "
        form = GameListForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_additional_games(), "GameA , GameB")

    def test_form_initialization_from_instance(self):
        self.owner2 = User.objects.create_user(username="owner2", password="testpass2")
        game_list = GameList.objects.create(
            owner=self.owner2,
            title="Existing List",
            description="Test description",
            game_guids=[self.game1.guid, self.game2.guid],
            additional_games="OtherGame",
            is_public=False,
        )
        form = GameListForm(instance=game_list)
        self.assertQuerySetEqual(
            form.fields["games"].initial.order_by("id"),
            Game.objects.filter(guid__in=game_list.game_guids).order_by("id"),
            transform=lambda x: x,
        )
        self.assertEqual(form.fields["additional_games"].initial, "OtherGame")

    def test_form_save_populates_game_guids(self):
        form = GameListForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        game_list = form.save(commit=False)
        game_list.owner = self.owner
        game_list.save()
        expected_guids = list(
            Game.objects.filter(id__in=[self.game1.id, self.game2.id]).values_list(
                "guid", flat=True
            )
        )
        self.assertEqual(game_list.game_guids, expected_guids)


class ListReviewFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="pass")
        self.list = GameList.objects.create(title="Sample List", owner=self.user)

        self.valid_data = {
            "title": "Solid picks",
            "rating": 4,
            "review_text": "I enjoyed most of these games.",
        }

    def test_valid_form(self):
        form = ListReviewForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_missing_fields(self):
        form = ListReviewForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("rating", form.errors)

    def test_rating_must_be_integer(self):
        data = self.valid_data.copy()
        data["rating"] = "invalid"
        form = ListReviewForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_widget_attributes(self):
        form = ListReviewForm()
        self.assertEqual(
            form.fields["title"].widget.attrs["placeholder"], "Review Title"
        )
        self.assertEqual(
            form.fields["review_text"].widget.attrs["placeholder"],
            "Write your review here...",
        )
        self.assertIsInstance(form.fields["rating"].widget.choices, list)


class PrivacySettingsFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="privacyuser", password="pass")
        self.prefs = self.user.userpreferences

    def test_valid_data(self):
        form = PrivacySettingsForm(
            data={
                "show_in_queue": True,
                "show_reviews": False,
                "show_favorites": True,
            },
            instance=self.prefs,
        )
        self.assertTrue(form.is_valid())
        prefs = form.save()
        self.assertTrue(prefs.show_in_queue)
        self.assertFalse(prefs.show_reviews)
        self.assertTrue(prefs.show_favorites)


class ListCommentFormTest(TestCase):
    def setUp(self):
        self.valid_data = {"text": "This is a comment about the list."}

    def test_valid_comment(self):
        form = ListCommentForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_empty_comment_invalid(self):
        form = ListCommentForm(data={"text": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)

    def test_widget_attributes(self):
        form = ListCommentForm()
        self.assertEqual(
            form.fields["text"].widget.attrs["placeholder"],
            "Write your comment here...",
        )
        self.assertEqual(form.fields["text"].widget.attrs["rows"], 4)


class PollFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "title": "Favorite Game Genre?",
            "description": "Choose your favorite genre.",
            "options": "Action\nAdventure\nRPG",
            "duration": 3,
            "is_public": True,
        }

    def test_poll_form_valid(self):
        form = PollForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        poll = form.save(commit=False)
        self.assertIsInstance(poll, Poll)
        self.assertEqual(poll.duration, timedelta(days=3))

    def test_poll_form_invalid_too_many_options(self):
        data = self.valid_data.copy()
        data["options"] = "\n".join([f"Option {i}" for i in range(1, 7)])
        form = PollForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("options", form.errors)

    def test_poll_form_missing_required_fields(self):
        form = PollForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("options", form.errors)
        self.assertIn("duration", form.errors)

    def test_poll_form_invalid_duration(self):
        data = self.valid_data.copy()
        data["duration"] = 10
        form = PollForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("duration", form.errors)


class VoteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

        self.poll = Poll.objects.create(
            title="Favorite color?",
            description="Test Desc",
            duration=timedelta(days=3),
            is_public=True,
            created_by=self.user,
        )

        self.option1 = PollOption.objects.create(poll=self.poll, text="Red")
        self.option2 = PollOption.objects.create(poll=self.poll, text="Blue")
        self.option3 = PollOption.objects.create(poll=self.poll, text="Green")

    def test_form_queryset_is_set_correctly(self):
        form = VoteForm(poll=self.poll)
        self.assertQuerySetEqual(
            form.fields["option"].queryset.order_by("id"),
            self.poll.options.all().order_by("id"),
            transform=lambda x: x,
        )

    def test_form_valid_with_valid_option(self):
        form_data = {"option": self.option2.pk}
        form = VoteForm(poll=self.poll, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["option"], self.option2)

    def test_form_invalid_with_option_not_in_poll(self):
        other_poll = Poll.objects.create(title="Another question?", created_by=self.user)
        other_option = PollOption.objects.create(poll=other_poll, text="Other option")

        form_data = {"option": other_option.pk}
        form = VoteForm(poll=self.poll, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("option", form.errors)

    def test_form_invalid_when_no_option_selected(self):
        form_data = {}
        form = VoteForm(poll=self.poll, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("option", form.errors)

    def test_form_queryset_empty_for_poll_with_no_options(self):
        empty_poll = Poll.objects.create(title="Empty poll", created_by=self.user)
        form = VoteForm(poll=empty_poll)
        self.assertEqual(form.fields["option"].queryset.count(), 0)


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_forms"])
    sys.exit(bool(failures))
