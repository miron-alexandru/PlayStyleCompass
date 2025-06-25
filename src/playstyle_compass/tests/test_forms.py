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



if __name__ == "__main__":
    import django
    import os
    import sys
    from django.conf import settings

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "playstyle_manager.settings")
    django.setup()

    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["playstyle_compass.tests.test_forms"])
    sys.exit(bool(failures))

