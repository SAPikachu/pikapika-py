from __future__ import unicode_literals, print_function

from .decorators import register_service, serialize_as_json

@register_service
@serialize_as_json
def hello_world(request):
    return "Hello world!"

