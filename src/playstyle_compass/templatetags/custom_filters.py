"""Custom filters."""


from datetime import datetime
from django import template
from itertools import zip_longest
from django.utils.translation import gettext

register = template.Library()


@register.filter(name="format_category_label")
def format_category_label(category):
    """Format a category label for better display."""
    category_labels = {
        "gaming_history": "gaming history",
        "favorite_genres": "favorite genres",
        "preferred_platforms": "preferred platforms",
        "common_genres_platforms": "common preferences",
    }

    return category_labels.get(category, category.replace("_", " "))


@register.filter(name="getattr")
def getattr_filter(obj, attr_name):
    """Get an attribute of an object with optional attribute name filtering."""
    if attr_name == "preferred_platforms":
        attr_name = "platforms"
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return ""


@register.filter(name="split_by_comma")
def split_by_comma(value):
    """Split a string by commas and return a list."""
    return value.split(", ")


@register.filter(name="is_favorite")
def is_favorite(game_id, user_favorites):
    if str(game_id) in user_favorites.split(","):
        return True
    return False


@register.filter(name="in_queue")
def in_queue(game_id, user_queue):
    if str(game_id) in user_queue.split(","):
        return True
    return False


@register.simple_tag
def zip_listse(reviewers, review_deck, review_text, score):
    if any([not reviewers, not review_deck, not review_text, not score]):
        return None
    else:
        zipped_data = zip_longest(
            reviewers.split(" [REV_SEP] "),
            review_deck.split(" [REV_SEP] "),
            review_text.split(" [REV_SEP] "),
            score.split(" [REV_SEP] "),
            fillvalue="N/A",
        )

        return zipped_data


@register.filter
def pluralize_reviews(count):
    return "review" if count == 1 else "reviews"


@register.filter(name="format_timestamp")
def format_timestamp(value):
    if isinstance(value, datetime):
        return value.isoformat()


@register.filter(name='template_trans')
def template_trans(text):
    try:
        return gettext(text)
    except Exception:
        return text