from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using square bracket notation in templates."""
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return None
