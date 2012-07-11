from __future__ import print_function, unicode_literals

import json

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import (
    HttpResponsePermanentRedirect, 
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
from django.contrib import admin
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse

from pikapika.common.decorators import staff_required, param_from_post
from pikapika.common.http import JsonResponseServerError, JsonResponse
from pikapika.novel.models import Volume, Chapter

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
    try:
        volume_id = int(volume_id)
    except ValueError:
        return HttpResponseBadRequest()

    volume = get_object_or_404(Volume, pk=volume_id)
    existing_chapters = list(volume.chapter_set.all())
    for client_chapter in json.loads(chapters_json):
        if existing_chapters:
            chapter_obj = existing_chapters.pop(0)
        else:
            chapter_obj = Chapter(volume=volume)
            chapter_obj.posted_by = request.user

        chapter_obj.name = client_chapter["name"]
        chapter_obj.content = json.dumps(client_chapter["lines"], indent=1)
        chapter_obj.save()

    if existing_chapters:
        [x.delete() for x in existing_chapters]

    volume.save()
    return JsonResponse({
        "return_url": reverse(
            "admin:novel_volume_change", 
            args={
                volume_id,
            },
        ),
    })

@admin.site.admin_view
def begin_edit(request, volume_id):
    volume = get_object_or_404(Volume, pk=volume_id)
    chapters = [
        {
            "name": x.name,
            "lines": json.loads(x.get_content() or "[]"),
        }
        for x in volume.chapter_set.all()
    ]
    return render(
        request,
        "novel_importer/begin_edit.html",
        {
            "volume_id": volume_id,
            "chapters": json.dumps(chapters),
        },
    )

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
