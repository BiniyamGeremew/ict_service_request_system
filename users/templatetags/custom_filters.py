# yourapp/templatetags/custom_filters.py
from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Add CSS class to a Django form field widget.
    Works with BoundField. If given a string, wraps it with a span.
    """
    try:
        existing_classes = field.field.widget.attrs.get('class', '')
        new_classes = f"{existing_classes} {css_class}".strip()
        return field.as_widget(attrs={**field.field.widget.attrs, 'class': new_classes})
    except AttributeError:
        # Fallback for plain strings
        return format_html('<span class="{}">{}</span>', css_class, field)

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Returns True if the user is in the given group.
    Usage: {% if request.user|has_group:"staff" %}
    """
    return user.groups.filter(name=group_name).exists()