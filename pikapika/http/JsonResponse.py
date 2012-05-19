from __future__ import unicode_literals, print_function

import json

from django.http import HttpResponse

class JsonResponse(HttpResponse):
    def __init__(self, obj, status=200):
        super(JsonResponse, self).__init__(
            json.dumps(obj),
            content_type="application/json; charset=utf-8",
            status=status,
        )
        
class JsonResponseError(JsonResponse):
    def __init__(self, message, status, **kwargs):
        result = {"message": message}
        result.update(kwargs)

        super(JsonResponseError, self).__init__(
            result,
            status=status,
        )

def _build_error_class(name, status):
    class _ErrorClass(JsonResponseError):
        def __init__(self, message, **kwargs):
            super(_ErrorClass, self).__init__(message, status, **kwargs)

    class_name = str("JsonResponse" + name)
    _ErrorClass.__name__ = class_name
    globals()[class_name] = _ErrorClass

_build_error_class("BadRequest", 400)
_build_error_class("ServerError", 500)

