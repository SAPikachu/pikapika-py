from __future__ import print_function, unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from pikapika.common.decorators import staff_required, param_from_post

@csrf_exempt
@require_POST
@staff_required
@param_from_post
def import_from_external(request, content_json, site_cookies_json):
    return render(
        request, 
        "novel_importer/import_from_external.html",
        {
            "content_json": content_json,
            "site_cookies_json": site_cookies_json,
        },
    )

@staff_required
def editor(request):
    return render(
        request, 
        "novel_importer/editor.html",
    )

def redirect_media(request, path):
    return HttpResponsePermanentRedirect(settings.MEDIA_URL + path)
