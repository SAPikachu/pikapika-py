# coding: utf-8
from __future__ import print_function, unicode_literals

from threading import local

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import linebreaks_filter
from django.shortcuts import get_object_or_404
from django.db.models import Max

from .models import Novel

# If we use relative URL, django will convert it into absolute URL using domain 
# specified in the sites framework.
# We don't want to hard-code the domain name, so we have to convert the URL
# ourselves.
# But Feed class does not provide request object to us, so here comes a hack.

class FeedBase(Feed):
    feed_type = Atom1Feed

    def __init__(self):
        super(FeedBase, self).__init__()
        self._local = local()

    def __call__(self, request, *args, **kwargs):
        self._local.request = request
        try:
            resp = super(FeedBase, self).__call__(request, *args, **kwargs)
        finally:
            self._local.request = None

        return resp

    @property
    def request(self):
        return self._local.request

    def reverse_absolute(self, *args, **kwargs):
        return self.request.build_absolute_uri(reverse(*args, **kwargs))

    def feed_url(self):
        return self.request.build_absolute_uri(self.request.path)

class LatestNovelsFeed(FeedBase):
    title = "最近更新 - PikaPika"

    def link(self):
        return self.reverse_absolute("index")

    def items(self):
        return (
            Novel.objects.all()
            [:settings.INDEX_LATEST_NOVELS_COUNT]
            .execute_with_latest_chapter()
        )

    def item_title(self, item):
        return "{} - {}".format(item.name, item.latest_chapter.volume.name)

    def item_description(self, item):
        # This must be HTML, can't be changed to text...
        return linebreaks_filter(item.description)

    def item_link(self, item):
        return self.reverse_absolute("details", kwargs={"pk": item.pk})

    def item_author_name(self, item):
        return item.author

    def item_pubdate(self, item):
        return item.updated_date

    def item_guid(self, item):
        return "urn:pikapika:novel:{};{}-{}".format(
            item.pk, item.latest_chapter.volume.pk, item.latest_chapter.pk
        )

class NovelVolumesFeed(FeedBase):
    def get_object(self, request, pk):
        return get_object_or_404(Novel, pk=int(pk))

    def title(self, obj):
        return obj.name + " - PikaPika"

    def link(self, obj):
        return self.reverse_absolute("details", kwargs={"pk": obj.pk})

    def items(self, obj):
        return (
            obj.volume_set.select_related("novel")
            .annotate(updated_date=Max("chapter__updated_date"))
            .order_by("-updated_date")
        )

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return linebreaks_filter(item.description)

    def item_link(self, item):
        return "{}#volume-{}".format(
            self.reverse_absolute("details", kwargs={"pk": item.novel.pk}),
            item.pk,
        )

    def item_author_name(self, item):
        return item.novel.author

    def item_pubdate(self, item):
        return item.updated_date

    def item_guid(self, item):
        return "urn:pikapika:volume:{}:{}".format(
            item.novel.pk, item.pk
        )
