"""Custom filters."""


from datetime import datetime
from django import template
from itertools import zip_longest
from django.utils.translation import gettext
from playstyle_compass.models import Franchise, Game


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

@register.filter
def pluralize_reviews(count):
    return "review" if count == 1 else "reviews"


@register.filter(name="format_timestamp")
def format_timestamp(value):
    if isinstance(value, datetime):
        return value.isoformat()


@register.filter(name="template_trans")
def template_trans(text):
    try:
        return gettext(text)
    except Exception:
        return text


@register.filter
def get_franchise_id(franchise_name):
    """Given a franchise name, return the id if it exists."""
    try:
        franchise = Franchise.objects.get(title=franchise_name)
        return franchise.id
    except Franchise.DoesNotExist:
        return None

    return None


@register.filter
def get_game_id(game_name):
    """Given a game name, return the id if it exists."""
    try:
        game = Game.objects.get(title=game_name)
        return game.id
    except Game.DoesNotExist:
        return None

    return None


@register.filter
def split_commas(value):
    return [item.strip() for item in value.split(',')]