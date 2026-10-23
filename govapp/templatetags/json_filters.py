"""Template filters for building GeoServer REST JSON."""

# Standard
import json

# Third-Party
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def json_string(value):
    """Returns the value as a complete JSON string, quotes included.

    json.dumps escapes quotes, backslashes, line breaks and other control
    characters as JSON requires. mark_safe stops Django's HTML autoescape,
    which would otherwise change the quotes to &quot;. None becomes "".
    """
    if value is None:
        value = ""
    return mark_safe(json.dumps(str(value)))
