from django import template
from django.forms.forms import BoundField

register = template.Library()


@register.filter(name="divide")
def divide(v1, v2):
    try:
        return float(v1) / float(v2)
    except (ValueError, ZeroDivisionError):
        return None
