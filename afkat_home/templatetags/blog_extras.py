import logging

from django import template
from django.contrib.auth import get_user_model
from django.utils.html import format_html


logger = logging.getLogger(__name__)

register = template.Library()
user_model = get_user_model()



@register.simple_tag()
def row(extra_classes=""):
    return format_html('<div class = "row {}">', extra_classes)


@register.simple_tag
def endrow():
    return format_html("</div>")


@register.simple_tag
def col(extra_classes=""):
    return format_html('<div class = "col {}">', extra_classes)


@register.simple_tag
def endcol():
    return format_html("</div>")

