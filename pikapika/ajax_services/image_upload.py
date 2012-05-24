from __future__ import unicode_literals, print_function

import os
import random
import string
from datetime import datetime
from io import BytesIO
from wsgiref.util import is_hop_by_hop
from urlparse import urlparse

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
import Image
import requests

from pikapika.common.http import (
    JsonResponseBadRequest, 
    JsonResponseServerError,
    utils as http_utils
)
from .decorators import register_service, generic_ajax_func
from pikapika.common.decorators import staff_required

FILE_NAME_FORMAT = "%Y%m%d-%H%M%S-{random}.{extension}"
RANDOM_LENGTH = 8
FORMAT_EXTENSION = {
    "JPEG": "jpg",
    "PNG": "png",
    "GIF": "gif",
}

def generate_file_path(extension):
    random_str = "".join(
        [random.choice(string.ascii_lowercase) for x in range(RANDOM_LENGTH)]
    )
    return datetime.now().strftime(os.path.join(
        settings.IMAGE_UPLOAD_DIR,
        FILE_NAME_FORMAT.format(random=random_str, extension=extension, )
    ))

@register_service
@staff_required
@generic_ajax_func
def upload_from_url(request, url, cookies):
    scheme, netloc, _, _, _, _ = urlparse(url.lower())
    if not scheme or not netloc:
        return JsonResponseBadRequest("Invalid URL")

    if scheme not in ("http", "https"):
        return JsonResponseBadRequest("Unsupported URL scheme")

    if netloc == request.get_host().lower():
        return JsonResponseBadRequest("Loopback is not allowed")

    if len(cookies) > 10240:
        return JsonResponseBadRequest("Cookie is too big")

    headers = {
        key[5:].replace("_", "-"): value
        for key, value in request.META.items()
        if key.startswith("HTTP_") and not key.startswith("HTTP_X_")
    }

    excluded_headers = [
        "ACCEPT", "ACCEPT-ENCODING", "COOKIE", "REFERER", "HOST"
    ]
    for key in list(headers.keys()):
        if is_hop_by_hop(key) or key in excluded_headers:
            del headers[key]

    headers["Cookie"] = cookies

    resp = requests.get(
        url, 
        headers=headers, 
        timeout=10,
    )
    resp.raise_for_status()

    size = int(resp.headers["content-length"])
    if size > 3 * 1024 * 1024:
        return JsonResponseBadRequest("The remote file is too big")

    content = resp.content
    if len(content) != size:
        return JsonResponseServerError("Connection terminated while downloading the file")

    file = File(BytesIO(content), name="")
    file.size = size
    return handle_image(file)

@register_service
@staff_required
@generic_ajax_func
def upload_from_local(request):
    if http_utils.is_form_request(request):
        file = request.FILES["file"]
    else:
        file = File(BytesIO(request.body), name="")
        # BytesIO doesn't provide size for us
        file.size = int(request.META["CONTENT_LENGTH"])

    if file is None:
        return JsonResponseBadRequest("There is no file in the request")

    return handle_image(file)

def handle_image(file):
    try:
        im = Image.open(file)
        im.verify()
        extension = FORMAT_EXTENSION.get(im.format, None)
        del im
        if not extension:
            return JsonResponseBadRequest("Unsupported image format")

        file_path = generate_file_path(extension)
        # Re-open the file to ensure position is at the beginning
        file.open()
        real_name = default_storage.save(file_path, file)
        return {
            "success": True,    
            "name": real_name,
        }
    except IOError:
        return JsonResponseBadRequest("Invalid image file")
