from __future__ import unicode_literals, print_function

import json

from django.http import HttpResponse

class JsonResponse(HttpResponse):
    def __init__(self, obj, status_code=200):
        super(JsonResponse, self).__init__(
            json.dumps(obj),
            content_type="application/json; charset=utf-8",
            status=status_code,
        )
