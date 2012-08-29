from __future__ import print_function, unicode_literals

from itertools import chain
import json
from math import ceil

from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Sum
from django.http import Http404

from . import models, chapter_utils
from .utils import first

INDEX_LATEST_NOVELS_COUNT = 15
NOVELS_PER_LIST_PAGE = 6

def index(request):
    latest_novels = (
        models.Novel.objects.all()
        [:INDEX_LATEST_NOVELS_COUNT]
        .execute_with_latest_chapter()
    )

    latest_novels.sort(key=lambda x: x.updated_date, reverse=True)

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
        with_hit_count().
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

def list_cat(request, cat_start=None, cat_end=None, page=None):
    if page:
        page = int(page)

    page = page or 1
    index = page - 1

    cat_start = cat_start.upper() if cat_start else None
    cat_end = cat_end.upper() if cat_end else None

    query = models.Novel.objects.all()
    if cat_start:
        query = (query.filter(cat_code__between=(cat_start, cat_end))
                 if cat_end
                 else query.filter(cat_code=cat_start))

    total_novels = query.count()
    total_pages = int(ceil(float(total_novels) / NOVELS_PER_LIST_PAGE))

    if total_novels:
        novels = (
            query
            .with_hit_count()
            [index * NOVELS_PER_LIST_PAGE:(index + 1) * NOVELS_PER_LIST_PAGE]
            .execute_with_latest_chapter()
        )

        if not novels:
            raise Http404()        

    else:
        novels = []

    return render(
        request,
        "novel/list.html",
        {
            "page": page,
            "cat_start": cat_start,
            "cat_end": cat_end,
            "novels": novels,
            "total_novels": total_novels,
            "total_pages": total_pages,
        },
    )

