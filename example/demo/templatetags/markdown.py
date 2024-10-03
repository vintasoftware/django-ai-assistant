from django import template
from django.utils.safestring import mark_safe

from pycmarkgfm import markdown_to_html


register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    if value is None:
        return ""
    return mark_safe(markdown_to_html(value))  # noqa: S308
