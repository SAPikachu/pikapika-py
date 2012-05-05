from pikapika.novel.models import *
from django.contrib import admin

class LinkedInline(admin.options.InlineModelAdmin):
    template = "admin/edit_inline/linked.html"
    extra = 0
    exclude = ("image", )
    class Media:
        js = (
            "js/jquery-1.7.2.min.js", 
            "js/jquery-ui-1.8.20.custom.min.js", 
            "js/ajax-call.js", 
            "js/activity-indicator.js", 
        )
        css = {
            "all": (
                "css/ui-lightness/jquery-ui-1.8.20.custom.css",
            ),
        }

class VolumeInline(LinkedInline):
    model = Volume

class NovelAdmin(admin.ModelAdmin):
    inlines = [VolumeInline]

admin.site.register(Novel, NovelAdmin)
admin.site.register(Volume)


