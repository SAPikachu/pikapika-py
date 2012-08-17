from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = patterns('pikapika.novel.views',
    url(r'^$', 
        'index', 
        name='index'),
    url(r'^novel/(?P<pk>\d+)(?:/.*)?$', 
        "details",
        name="details"),
    url(r'^read/(?P<pk>\d+)(?:/.*)?$', 
        "read", 
        name="read"),
)
