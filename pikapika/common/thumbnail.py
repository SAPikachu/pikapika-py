from __future__ import print_function, unicode_literals

import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views import static
import Image

ROOT = settings.MEDIA_ROOT
OUTPUT_PATH_FORMAT = "{path}.thumb.{max_width}_{max_height}.jpg"

def generate(request, path, max_width, max_height):
    output_path = OUTPUT_PATH_FORMAT.format(
        path=path,
        max_width=max_width,
        max_height=max_height,
    )
    output_path_full = os.path.join(ROOT, output_path)

    try:
        if not os.path.isfile(output_path_full):
            im = Image.open(os.path.join(ROOT, path))
            im.thumbnail((int(max_width), int(max_height)), Image.ANTIALIAS)
            temp = NamedTemporaryFile(
                dir=os.path.dirname(output_path_full),
                delete=False,
            )
            temp_name = temp.name
            with temp:
                im.save(temp, "JPEG")

            try:
                os.rename(temp_name, output_path_full)
            except (IOError, OSError):
                assert os.path.isfile(output_file)
                os.remove(temp_name)

        # After generation, it should be directly served via mod_rewrite
        return static.serve(request, output_path, document_root=ROOT)
    except IOError:
        return HttpResponseNotFound()
        
