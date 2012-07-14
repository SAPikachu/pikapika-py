from __future__ import print_function, unicode_literals

from django import template
from django.conf import settings

register = template.Library()

STATIC_VERSION = "0"

@register.simple_tag
def css(name, media="", outside_css=False):
    if "://" not in name and not outside_css:
        name = "css/{}?{}".format(name, STATIC_VERSION)

    name = settings.STATIC_URL + name

    return '<link type="text/css" rel="stylesheet" href="{}" {}/>'.format(
        name,
        'media="{}"'.format(media) if media else "",
    )
