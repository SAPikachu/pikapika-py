from __future__ import unicode_literals, print_function

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation
from django.conf import settings
from cjklib.characterlookup import CharacterLookup
from hitcount.models import HitCount

from .managers import NovelManager

IMAGE_UPLOAD_DIR = settings.IMAGE_UPLOAD_DIR

def get_cat_code(s):
    char = unicode(s)[0]

    cjk = CharacterLookup("C")
    readings = cjk.getReadingForCharacter(char, "Pinyin")
    if not readings:
        # Not Chinese, just use first character as code
        return char.upper()

    # It's very hard to determine which reading is correct for our case,
    # so don't bother to check it, just use the first one and let users to fix
    # it if it is incorrect
    reading = readings[0]
    
    # We use the first letter as code
    return reading[0].upper()

class Novel(models.Model):
    name = models.CharField(max_length=512)
    cat_code = models.CharField(max_length=5)
    description = models.TextField()
    author = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    image = models.ImageField(upload_to=IMAGE_UPLOAD_DIR, blank=True)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    updated_date = models.DateTimeField(auto_now=True)

    objects = NovelManager()

    class Meta:
        get_latest_by = "updated_date"
        ordering = ["-updated_date", "-pk"]

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.cat_code:
            self.cat_code = get_cat_code(self.name)

        super(Novel, self).save(*args, **kwargs)

class Volume(models.Model):
    name = models.CharField(max_length=512)
    novel = models.ForeignKey(Novel)
    description = models.TextField()
    image = models.ImageField(upload_to=IMAGE_UPLOAD_DIR, blank=True)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)

    class Meta:
        order_with_respect_to = "novel"
    
    def __unicode__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=512)
    volume = models.ForeignKey(Volume)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    updated_date = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User)
    hitcount_object = GenericRelation(HitCount, object_id_field="object_pk")

    def get_content(self):
        try:
            return self.content_record.content
        except ChapterContent.DoesNotExist:
            return ""

    def set_content(self, content):
        content_record = None
        try:
            content_record = self.content_record
        except ChapterContent.DoesNotExist:
            pass

        if not content_record:
            content_record = ChapterContent(chapter=self)
            self.content_record = content_record

        content_record.content = content
        self._content_dirty = True

    content = property(get_content, set_content)

    @property
    def hitcount_object_safe(self):
        if not hasattr(self, "_hitcount_object_safe"):
            self._hitcount_object_safe = HitCount.objects.get_for_object(self)

        return self._hitcount_object_safe

    def get_hit_count(self):
        return self.hitcount_object_safe.hits

    def set_hit_count(self, hits):
        self.hitcount_object_safe.hits = hits
        self.hitcount_object_safe.save()

    hit_count = property(get_hit_count, set_hit_count)

    class Meta:
        order_with_respect_to = "volume"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Chapter, self).save(*args, **kwargs)

        if self._content_dirty:
            # Ensure content_record.chapter_id is set
            self.content_record.chapter = self

            self.content_record.save()
            self._content_dirty = False

        self.volume.novel.save()
              
    def __init__(self, *args, **kwargs):
        super(Chapter, self).__init__(*args, **kwargs)
        self._content_dirty = False

class ChapterContent(models.Model):
    chapter = models.OneToOneField(Chapter, related_name="content_record")
    content = models.TextField()

