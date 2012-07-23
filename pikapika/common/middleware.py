from __future__ import print_function, unicode_literals

from django.utils.http import http_date
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.contrib.staticfiles.handlers import StaticFilesHandler

def process(request, response):
    if (request.META.get("HTTP_X_LIVE_JS", 0) or 
        "live=1" in request.META.get("HTTP_REFERER", "")):
        response["Pragma"] = "no-cache"
        response["Cache-Control"] = "no-cache"
        response["Expires"] = http_date()

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
