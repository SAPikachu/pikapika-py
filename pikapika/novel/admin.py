from pikapika.novel.models import *
from django.contrib import admin

class LinkedInline(admin.options.InlineModelAdmin):
    template = "admin/edit_inline/linked.html"
    extra = 0
    exclude = ("image", )
    class Media:
        js = ("js/jquery-ui-1.8.20.custom.min.js", )

class VolumeInline(LinkedInline):
    model = Volume

class NovelAdmin(admin.ModelAdmin):
    inlines = [VolumeInline]

admin.site.register(Novel, NovelAdmin)
admin.site.register(Volume)


