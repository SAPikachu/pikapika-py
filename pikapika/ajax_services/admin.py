from __future__ import unicode_literals, print_function

from .decorators import register_service, generic_ajax_func

@register_service
@generic_ajax_func
def hello_world(request, p):
    return "Hello world! " + p

