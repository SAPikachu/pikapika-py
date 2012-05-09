from pikapika.novel.models import *
from django.contrib import admin

from django.conf import settings

GRAPPELLI_INSTALLED = "grappelli" in settings.INSTALLED_APPS

class SubmodelInline(admin.options.InlineModelAdmin):
    template = "admin/edit_inline/submodel.html"
    extra = 0
    exclude = ("image", )
    class Media:
        # grappelli is shipped with jquery-ui, avoid conflicting here
        js = \
            (
                "js/jquery-ui-1.8.20.custom.min.js", 
            ) if not GRAPPELLI_INSTALLED else (
                "admin/js/jquery.init.js",
            ) 

        js += \
            (
                "js/ajax-call.js", 
                "js/activity-indicator.js", 
                "js/admin/submodel-inline.js", 
            )

        if not GRAPPELLI_INSTALLED:
            css = {
                "all": (
                    "css/ui-lightness/jquery-ui-1.8.20.custom.css",
                ),
            }

class VolumeInline(SubmodelInline):
    model = Volume

class NovelAdmin(admin.ModelAdmin):
    inlines = [VolumeInline]

admin.site.register(Novel, NovelAdmin)
admin.site.register(Volume)


