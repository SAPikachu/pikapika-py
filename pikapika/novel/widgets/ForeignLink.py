from django.forms.widgets import HiddenInput
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.core import urlresolvers

class ForeignLinkWidget(HiddenInput):
    def __init__(self, rel_class):
        super(ForeignLinkWidget, self).__init__()
        self.rel_class = rel_class

    def render(self, name, value, **kwargs):
        """ Renders a link to change page of the related model """

        # Keep the field in the form for POSTing
        result = super(ForeignLinkWidget, self).render(
            name, value, **kwargs
        )
        label = None
        for id, label in self.choices:
            if value == id:
                label = conditional_escape(force_unicode(label))
                break

        if label:
            # The outer <label> is for styling
            result += u'<label><a href="{url}">{label}</a></label>'.format(
                url=urlresolvers.reverse(
                    "admin:{}_{}_change".format(
                        self.rel_class._meta.app_label,
                        self.rel_class._meta.module_name,
                    ),
                    args=(value,),
                ),
                label=label,
            )

        return mark_safe(result)

