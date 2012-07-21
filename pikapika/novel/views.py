from __future__ import print_function, unicode_literals

from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Sum

from . import models

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
    query = (
        models.Novel.objects.
        filter(pk=int(pk)).
        annotate(hit_count=Sum("volume__chapter__hit_records__hits"))
    )
    novel = get_object_or_404(query)
    return render(
        request,
        "novel/details.html",
        {
            "novel": novel,
        },
    )
