from django import template

register = template.Library()

CUSTOM_FORMATTING = {
    'rpg': 'Role-playing (RPG)',
    'pc': 'PC',
    'vr': 'Virtual Reality (VR)',
}

@register.filter(name='format_preferences')
def format_preferences(value):
    formatted_preferences = []

    for preference in value.split(', '):
        if preference in CUSTOM_FORMATTING:
            formatted_preferences.append(CUSTOM_FORMATTING[preference])
        else:
            formatted_preference = preference.capitalize()
            formatted_preferences.append(formatted_preference)

    return ', '.join(formatted_preferences)
