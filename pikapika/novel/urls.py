from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="base.html"), name="index"),
)
