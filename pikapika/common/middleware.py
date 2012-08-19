# Don't import unicode_literals here, otherwise set_cookie / delete_cookie will fail (as of django 1.4)
from __future__ import print_function

import hashlib

from django.utils.http import http_date
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.contrib.staticfiles.handlers import StaticFilesHandler

def process(request, response):
    if request.GET.get("live", None) == "0":
        response.delete_cookie("live")
    elif (request.COOKIES.get("live", False) or
        request.GET.get("live", False)):

        response.set_cookie("live", "1", max_age=24*60*60)

        response["Pragma"] = "no-cache"
        response["Cache-Control"] = "no-cache"
        response["Expires"] = http_date()
        if "ETag" not in response:
            response["ETag"] = '"{}"'.format(
                hashlib.md5(response.content).hexdigest()
            )

    return response

def patch_static_handler():
    # Static files won't go through middleware pipeline, so we have to do this
    old_serve = StaticFilesHandler.serve

    def _patched_serve(self, request):
        return process(request, old_serve(self, request))

    StaticFilesHandler.serve = _patched_serve

if settings.DEBUG:
    patch_static_handler()

class LiveJsMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed()

    def process_response(self, request, response):
        return process(request, response)
