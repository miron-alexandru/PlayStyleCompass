"""Custom filters."""

import difflib
import re
from datetime import datetime
from django import template
from itertools import zip_longest
from django.utils.translation import gettext as _
from django.apps import apps
from django.urls import reverse
from pytz import timezone
from django.utils import timezone as django_timezone
from django.utils.safestring import mark_safe
from ..models import Game, Franchise, Character
from django.http import QueryDict


register = template.Library()


@register.filter(name="format_category_label")
def format_category_label(category):
    """Format a category label for better display."""
    category_labels = {
        "gaming_history": _("gaming history"),
        "favorite_genres": _("favorite genres"),
        "themes": _("favorite themes"),
        "preferred_platforms": _("preferred platforms"),
        "common_genres_platforms": _("common preferences"),
    }

    return category_labels.get(category, _(category.replace("_", " ")))


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
    if value:
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


@register.filter(name="template_trans")
def template_trans(text):
    try:
        return _(text)
    except Exception:
        return text


@register.filter
def get_object_id(object_name, model_name):
    """
    Given an object name and a model, return the ID if it exists.
    """
    model = apps.get_model(app_label="playstyle_compass", model_name=model_name)
    try:
        if model_name == "Character":
            objs = model.objects.filter(name=object_name)
        else:
            objs = model.objects.filter(title=object_name)

        if objs.exists():
            if model_name == "Game":
                return objs.first().guid
            elif objs.count() == 1:
                return objs.first().id
            else:
                return [obj.id for obj in objs]
        else:
            return None
    except ObjectDoesNotExist:
        return None


@register.filter
def split_commas(value):
    return [item.strip() for item in value.split(",")]


@register.filter
def check_platform(platform, user_platforms):
    """Filter to check if a platform is present in the user preferences."""
    # Note:
    """This filter is used because checking with the "in" operator
    always returns True for the 'PlayStation' platform when the user has 
    'PlayStation 5' or 'PlayStation 4' in their preferrences."""
    if not "," in user_platforms:
        return platform == user_platforms
    else:
        return platform in user_platforms


@register.filter
def convert_to_user_timezone(timestamp, user_timezone):
    timestamp = django_timezone.localtime(timestamp)
    user_tz = timezone(user_timezone)
    timestamp_in_user_tz = timestamp.astimezone(user_tz)
    formatted_timestamp = timestamp_in_user_tz.strftime("%B %d, %Y, %I:%M %p")

    return formatted_timestamp


@register.filter
def bold_requirements(value):
    """Filter used to make requirements in bold."""
    if value:
        requirements = [
            "Processor:",
            "OS:",
            "OS \\*:",
            "Memory:",
            "Graphics:",
            "DirectX:",
            "Storage:",
            "Sound Card:",
            "Additional Notes:",
        ]
        for req in requirements:
            value = re.sub(f"({req})", r"<strong>\1</strong>", value)

        return mark_safe(value)
    return None


@register.filter
def game_link(game_name):
    """This filter generates hyperlinks for games based on a provided game name.
    It retrieves the closest match to the provided name from the database.
    """
    game_titles = Game.objects.values_list("title", flat=True)
    game_name_lower = game_name.lower()

    # Find the closest match
    closest_matches = difflib.get_close_matches(
        game_name_lower, [title.lower() for title in game_titles], n=1, cutoff=0.70
    )

    if closest_matches:
        closest_match = closest_matches[0]
        try:
            game = Game.objects.get(title__iexact=closest_match)
            url = reverse("playstyle_compass:view_game", args=[game.guid])
            return f'<a href="{url}">{game_name}</a>'
        except Game.DoesNotExist:
            return game_name
    else:
        return game_name


@register.filter
def object_link(name, object_type):
    """This filter generates hyperlinks for objects
    based on a provided name and object type.
    It retrieves the closest match to the provided name from the database
    """
    name_lower = name.lower()

    if object_type == "franchise":
        titles = Franchise.objects.values_list("title", flat=True)
        titles_lower = [title.lower() for title in titles]
        url_name = "playstyle_compass:franchise"
        model = Franchise
    elif object_type == "character":
        names = Character.objects.values_list("name", flat=True)
        names_lower = [char_name.lower() for char_name in names]
        url_name = "playstyle_compass:character"
        model = Character
    else:
        return name

    closest_matches = difflib.get_close_matches(
        name_lower,
        titles_lower if object_type == "franchise" else names_lower,
        n=1,
        cutoff=0.70,
    )

    if closest_matches:
        closest_match_lower = closest_matches[0]
        try:
            if object_type == "franchise":
                closest_match = next(
                    title for title in titles if title.lower() == closest_match_lower
                )
                obj = model.objects.get(title__iexact=closest_match)
            else:
                closest_match = next(
                    char_name
                    for char_name in names
                    if char_name.lower() == closest_match_lower
                )
                obj = model.objects.get(name__iexact=closest_match)

            url = reverse(url_name, args=[obj.id])
            return f'<a href="{url}">{name}</a>'
        except model.DoesNotExist:
            return name
    else:
        return name


@register.simple_tag
def querystring_replace(request, **kwargs):
    query_string = request.GET.urlencode()
    query_dict = QueryDict(query_string, mutable=True)
    for key, value in kwargs.items():
        if value is None:
            query_dict.pop(key, None)
        else:
            query_dict[key] = value
    return query_dict.urlencode()
