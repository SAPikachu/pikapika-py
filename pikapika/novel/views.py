from __future__ import print_function, unicode_literals

from itertools import chain
import json

from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Sum

from . import models, chapter_utils
from .utils import first

INDEX_LATEST_NOVELS_COUNT = 15

def index(request):
    latest_novels_prep = {
        x.latest_chapter_id: x for x in
        models.Novel.objects.
        order_by("-updated_date").
        annotate(latest_chapter_id=Max("volume__chapter__id")).
        filter(latest_chapter_id__gt=0)
        [:INDEX_LATEST_NOVELS_COUNT]
    }

    chapters = (
        models.Chapter.objects.
        filter(pk__in=latest_novels_prep.keys()).
        select_related("volume")
    )

    latest_novels = [
        {
            "novel": latest_novels_prep[x.pk],
            "chapter": x,
        }
        for x in chapters
    ]

    latest_novels.sort(key=lambda x: x["novel"].updated_date, reverse=True)

    return render(
        request,
        "novel/index.html",
        {
            "latest_novels": latest_novels,
        },
    )

def details(request, pk):
    pk = int(pk)

    query = (
        models.Novel.objects.
        filter(pk=pk).
        annotate(hit_count=Sum("volume__chapter__hit_records__hits")).
        prefetch_related("volume_set__chapter_set")
    )
    novel = get_object_or_404(query)
    novel.latest_chapter = max(
        chain.from_iterable((
            vol.chapter_set.all()
            for vol in novel.volume_set.all()
        )),
        key=lambda chap: chap.updated_date,
    )
    return render(
        request,
        "novel/details.html",
        {
            "novel": novel,
        },
    )

def read(request, pk):
    pk = int(pk)
    chapter = get_object_or_404(
        models.Chapter.objects.
            annotate(hit_count=Sum("hit_records__hits")).
            filter(pk=pk)
    )
    prev_chapter = None
    try:
        prev_chapter = chapter.get_previous_in_order()
    except models.Chapter.DoesNotExist:
        try:
            prev_volume = chapter.volume.get_previous_in_order()
            prev_chapter = (
                first(prev_volume.chapter_set.reverse()[:1], default=None)
            )
        except models.Volume.DoesNotExist:
            pass

    next_chapter = None
    try:
        next_chapter = chapter.get_next_in_order()
    except models.Chapter.DoesNotExist:
        try:
            next_volume = chapter.volume.get_next_in_order()
            next_chapter = (
                first(next_volume.chapter_set[:1], default=None)
            )
        except models.Volume.DoesNotExist:
            pass

    rendered_chapter = chapter_utils.render(json.loads(chapter.content))

    return render(
        request,
        "novel/read.html",
        {
            "chapter": chapter,
            "rendered_chapter": rendered_chapter,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter,
        },
    )
