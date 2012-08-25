from __future__ import unicode_literals, print_function

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cjklib.characterlookup import CharacterLookup

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
              
    def __init__(self, *args, **kwargs):
        super(Chapter, self).__init__(*args, **kwargs)
        self._content_dirty = False

class ChapterContent(models.Model):
    chapter = models.OneToOneField(Chapter, related_name="content_record")
    content = models.TextField()

class HitCountRecord(models.Model):
    chapter = models.ForeignKey(
        Chapter, 
        unique_for_date="date", 
        related_name="hit_records",
    )
    date = models.DateField(auto_now_add=True)
    hits = models.IntegerField(default=1)

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    novel = models.ForeignKey(Novel)

    def __unicode__(self):
        return self.tag

