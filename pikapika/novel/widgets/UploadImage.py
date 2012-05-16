from __future__ import unicode_literals, print_function

from django.forms.widgets import TextInput
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage

MEDIA_PREFIX = "modules/file-uploader/"

class UploadImageWidget(TextInput):
    class Media:
        css = {
            "all": (MEDIA_PREFIX + "fileuploader.css", )
        }
        js = (
            "js/jquery.cookie.js",
            MEDIA_PREFIX + "fileuploader.js", 
        )

    def __init__(self, attrs=None):
        final_attrs = {"class": "vTextField"}
        final_attrs.update(attrs or {})

        super(UploadImageWidget, self).__init__(attrs=final_attrs)

    def render(self, name, value, attrs=None, **kwargs):
        super_render = super(UploadImageWidget, self).render(
            name, value, attrs, **kwargs
        )
        final_attrs = self.build_attrs(attrs)
        return mark_safe(render_to_string("widgets/UploadImage.html", {
            "super": super_render,
            "name": name,
            "value": value,
            "attrs": final_attrs,
        }))

    def value_from_datadict(self, *args, **kwargs):
        value = super(UploadImageWidget, self). \
                value_from_datadict(*args, **kwargs)

        if value:
            return default_storage.open(value)

        return None

