from __future__ import print_function, unicode_literals

from django import template
from django.conf import settings

register = template.Library()

STATIC_VERSION = "0"

def get_asset_url(name, prefix, outside):
    is_abs = "://" in name
    if not is_abs and not outside:
        name = "{}/{}?{}".format(prefix, name, STATIC_VERSION)

    if not is_abs:
        name = settings.STATIC_URL + name

    return name

@register.simple_tag
def css(name, media="", outside=False):
    return '<link type="text/css" rel="stylesheet" href="{}" {}/>'.format(
        get_asset_url(name, "css", outside),
        'media="{}"'.format(media) if media else "",
    )

@register.simple_tag
def js(name, outside=False):
    return '<script type="text/javascript" src="{}"></script>'.format(
        get_asset_url(name, "js", outside),
    )
