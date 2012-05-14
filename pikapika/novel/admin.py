import pdb

from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.forms import ModelForm
from django.conf import settings
from django.db import models

from pikapika.novel.models import *
from pikapika.novel.widgets import ForeignLinkWidget, UploadImageWidget

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

class AdminBase(admin.ModelAdmin):
    formfield_overrides = {
        models.ImageField: {"widget": UploadImageWidget},
    }
    def formfield_for_dbfield(self, db_field, **kwargs):
        result = super(AdminBase, self).formfield_for_dbfield(db_field, **kwargs)

        # We want foreign keys to models that are created by us be immutable
        # after creation, so we replace it with a link
        if db_field.rel and hasattr(kwargs["request"], "is_change_view"):
            rel_class = db_field.rel.to
            if __package__.endswith(rel_class._meta.app_label):
                result.widget = ForeignLinkWidget(rel_class)

        return result

    def change_view(self, request, *args, **kwargs):
        # For use in formfield_for_dbfield
        request.is_change_view = True
        return super(AdminBase, self).change_view(request, *args, **kwargs)


class NovelAdmin(admin.ModelAdmin):
    inlines = [VolumeInline]

class VolumeAdmin(AdminBase):
    inlines = [ChapterInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for inst in instances:
            if isinstance(inst, Chapter) and not inst.posted_by_id:
                inst.posted_by = request.user

            inst.save()

class ChapterAdmin(AdminBase):
    inlines = [ChapterContentInline]

admin.site.register(Novel, NovelAdmin)
admin.site.register(Volume, VolumeAdmin)
admin.site.register(Chapter, ChapterAdmin)


