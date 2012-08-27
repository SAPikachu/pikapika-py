from __future__ import print_function, unicode_literals

from django.db import models
from django.db.models import Max, Sum
from django.db.models.query import QuerySet

class NovelManager(models.Manager):
    def get_query_set(self):
        return NovelQuerySet(self.model, using=self._db)

class NovelQuerySet(QuerySet):
    def with_hit_count(self):
        return self.annotate(
            hit_count=Sum("volume__chapter__hit_records__hits")
        )

    def execute_with_latest_chapter(self, exclude_novel_without_chapter=True):
        # Import here to prevent circular importing
        from .models import Chapter

        query = self.annotate(latest_chapter_id=Max("volume__chapter__id"))
        if exclude_novel_without_chapter:
            limit = query.query.low_mark, query.query.high_mark
            query.query.clear_limits()
            query = query.filter(latest_chapter_id__gt=0)
            query.query.low_mark, query.query.high_mark = limit
        
        result = list(query)
        chapter_ids = [x.latest_chapter_id for x in result]
        chapters = {
            x.pk: x for x in
            Chapter.objects.filter(pk__in=chapter_ids).
            select_related("volume")
        }

        for novel in result:
            if novel.latest_chapter_id:
                novel.latest_chapter = chapters[novel.latest_chapter_id]

        return result
