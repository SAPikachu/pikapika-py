from __future__ import print_function, unicode_literals

from datetime import timedelta

from django.db import models
from django.db.models import Max, Sum, Count
from django.db.models.query import QuerySet
from django.utils import timezone
from generic_aggregation import generic_annotate
from hitcount.models import HitCount, Hit

# Note: Only import novel models inside method to prevent circular importing

class NovelManager(models.Manager):
    def get_query_set(self):
        return NovelQuerySet(self.model, using=self._db)

class NovelQuerySet(QuerySet):
    def with_hit_count(self):
        from .models import Chapter
        return generic_annotate(
            self,
            HitCount,
            Sum("volume__chapter__hitcount_object__hits"),
            alias="hit_count",
            force_rel_model=Chapter,
        )

    def with_hit_count_last_week(self):
        from .models import Chapter
        from django.db import connections
        return generic_annotate(
            self,
            HitCount,
            Count("volume__chapter__hitcount_object__hit__created"),
            alias="hit_count_last_week",
            force_rel_model=Chapter,
            rel_slice_pos=-2,
        ).extra(where=[Hit._meta.db_table + ".created > %s"], 
                params=[connections[self.db].ops.value_to_db_datetime(
                            timezone.now() - timedelta(days=7)
                       )],
               )

    def execute_with_latest_chapter(self, exclude_novel_without_chapter=True):
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
