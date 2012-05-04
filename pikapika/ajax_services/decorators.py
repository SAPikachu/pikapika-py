import json
from functools import update_wrapper

from django.conf.urls import patterns, include, url
from django.http import HttpResponse

from .urls import urlpatterns

def serialize_as_json(func):
    def _wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, HttpResponse):
            return result

        return HttpResponse(
            json.dumps(result),
            content_type="application/json; charset=utf-8",
        )
    
    wrapped = update_wrapper(_wrap, func)
    return _wrap

def get_prefix_for_module_name(module_name):
    # module_name looks like: pikapika.ajax_services.module
    # __name__ looks like: pikapika.ajax_services.decorators

    parts = module_name.split(".")
    common_prefix = __name__.split(".")[:-1]

    while common_prefix:
        assert parts[0] == common_prefix[0]
        parts.pop(0)
        common_prefix.pop(0)

    assert parts
    return "/".join(parts)

def register_service(func):
    global urlpatterns
    urlpatterns += patterns(
        '', 
        url(
            r"^{}/{}$".format(
                get_prefix_for_module_name(func.__module__), 
                func.__name__,
            ), 
            func,
        ),
    )
    return func

