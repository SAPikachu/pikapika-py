from __future__ import print_function, unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from pikapika.common.decorators import staff_required, param_from_post

@csrf_exempt
@staff_required
@param_from_post
def import_from_external(request, content_json, site_cookies):
    return render(
        request, 
        "novel_importer/import_from_external.html",
        {
            "content_json": content_json,
            "site_cookies": site_cookies,
        },
    )
