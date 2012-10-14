from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView

from .feeds import LatestNovelsFeed, NovelVolumesFeed

urlpatterns = patterns('pikapika.novel.views',
    url(r'^$', 
        'index', 
        name='index'),
    url(r'^feed$', 
        LatestNovelsFeed(),
        name='latest_novels_feed'),
    url(r'^list(?:/(?P<cat_start>[A-Za-z])(?:-(?P<cat_end>[A-Za-z]))?)?(?:/(?P<page>\d+))?/?$', 
        "list_cat",
        name="list"),
    url(r'^novel/(?P<pk>\d+)/feed$',
        NovelVolumesFeed(),
        name='novel_volumes_feed'),
    url(r'^novel/(?P<pk>\d+)(?:/.*)?$', 
        "details",
        name="details"),
    url(r'^read/(?P<pk>\d+)(?:/.*)?$', 
        "read", 
        name="read"),

    url(r'^Novel/Details/(?P<pk>\d+)(?:/.*)?$', 
        'redirect_old_link',
        {'view_name': 'details'},),
    url(r'^Novel/Read/(?P<pk>\d+)(?:/.*)?$', 
        'redirect_old_link',
        {'view_name': 'read'},),
    url(r'^Novel/List(?:/.*)?$', 
        'redirect_old_link',
        {'view_name': 'list'},),
)
