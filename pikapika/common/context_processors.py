from __future__ import print_function, unicode_literals

from django.conf import settings

def misc(request):
    return {
        "load_live_js": 
            settings.DEBUG and 
            (request.GET.get("live", False) not in ("0", False) or 
             request.COOKIES.get("live", False)),
    }
