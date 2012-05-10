from pikapika.novel.models import *
from django.contrib import admin

from django.conf import settings

GRAPPELLI_INSTALLED = "grappelli" in settings.INSTALLED_APPS

class SubmodelInline(admin.options.InlineModelAdmin):
    template = "admin/edit_inline/submodel.html"
    extra = 0
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
    exclude = ("image", )

class ChapterInline(SubmodelInline):
    exclude = ("posted_by", )
    model = Chapter

class ChapterContentInline(admin.TabularInline):
    model = ChapterContent

class NovelAdmin(admin.ModelAdmin):
    inlines = [VolumeInline]

class VolumeAdmin(admin.ModelAdmin):
    inlines = [ChapterInline]
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for inst in instances:
            if isinstance(inst, Chapter) and not inst.posted_by_id:
                inst.posted_by = request.user

            inst.save()

class ChapterAdmin(admin.ModelAdmin):
    inlines = [ChapterContentInline]

admin.site.register(Novel, NovelAdmin)
admin.site.register(Volume, VolumeAdmin)
admin.site.register(Chapter, ChapterAdmin)


