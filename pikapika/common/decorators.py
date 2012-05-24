from functools import wraps

from django.http import HttpResponse, HttpResponseForbidden

from pikapika.common.http import JsonResponse, utils as http_utils

def staff_required(func):
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

        return JsonResponse(result)

    return _wrap

def param_from_post(func):
    @wraps(func)
    def _wrap(request):
        kwargs = {}
        if http_utils.is_form_request(request):
            kwargs.update(request.POST.dict())

        return func(request=request, **kwargs)

    return _wrap

