from django import template

register = template.Library()

@register.filter(name='format_category_label')
def format_category_label(category):
    category_labels = {
        'gaming_history': 'gaming history',
        'favorite_genres': 'favorite genres',
        'preferred_platforms': 'preferred platforms',
        'common_genres_platforms': 'common preferences',
    }
    
    return category_labels.get(category, category.replace('_', ' '))


@register.filter(name='getattr')
def getattr_filter(obj, attr_name):
    if attr_name == 'preferred_platforms':
        attr_name = 'platforms'
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return ''