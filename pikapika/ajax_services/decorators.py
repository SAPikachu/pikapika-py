import json
from functools import wraps

from django.conf.urls import patterns, include, url
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .urls import urlpatterns

def require_staff(func):
    @wraps(func)
    def _wrap(request):
        if request.user.is_active and request.user.is_staff:
            return func(request)
        else:
            return HttpResponseForbidden()

    return _wrap

def serialize_as_json(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, HttpResponse):
            return result

        return HttpResponse(
            json.dumps(result),
            content_type="application/json; charset=utf-8",
        )
    
    return _wrap

def param_from_post(func):
    @wraps(func)
    def _wrap(request):
        return func(request=request, **request.POST.dict())

    return _wrap

def generic_ajax_func(func):
    return require_POST(
        csrf_protect(
            serialize_as_json(
                param_from_post(
                    func
                )
            )
        )
    )

def _get_prefix_for_module_name(module_name):
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
                _get_prefix_for_module_name(func.__module__), 
                func.__name__,
            ), 
            func,
        ),
    )
    return func

