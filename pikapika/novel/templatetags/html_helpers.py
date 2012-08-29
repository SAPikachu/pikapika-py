from __future__ import print_function, unicode_literals

import re

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

@register.simple_tag
def requirejs(name):
    return """
<script type="text/javascript">var require = {{ baseUrl: "{base}" }};</script>
<script type="text/javascript" src="{base}/require.js" data-main="{name}"></script>
""".format(
        base=settings.STATIC_URL + "js",
        name=name,
    )

@register.filter
def normalize_whitespace(value):
    return re.sub(r"\s+", " ", value, flags=re.S)
