from __future__ import print_function, unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound
from django.contrib import admin
from django.template import TemplateDoesNotExist

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

@require_POST
@staff_required
@param_from_post
def save_volume_ajax(request, volume_id, chapters_json):
    raise NotImplemented

@admin.site.admin_view
def static_view(request, page_name):
    try:
        return render(
            request, 
            "novel_importer/static/{}.html".format(page_name),
        )
    except TemplateDoesNotExist:
        return HttpResponseNotFound()

def redirect_media(request, path):
    return HttpResponsePermanentRedirect(settings.MEDIA_URL + path)
