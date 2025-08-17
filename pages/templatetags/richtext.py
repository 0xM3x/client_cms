from django import template
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()

# Configure once; reset per convert for clean state
_md = md.Markdown(extensions=["extra", "sane_lists", "smarty"])

@register.filter(name="render_md")
def render_md(value: str):
    html = _md.reset().convert(value or "")
    return mark_safe(html)

