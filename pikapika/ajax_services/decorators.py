
from django.conf.urls import patterns, include, url
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .urls import urlpatterns
from pikapika.common.decorators import serialize_as_json, param_from_post

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

