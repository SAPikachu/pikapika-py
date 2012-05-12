from __future__ import unicode_literals, print_function

from django.db import models
from django.contrib.auth.models import User
from cjklib.characterlookup import CharacterLookup

IMAGE_DIR = "images/%Y/%m/%d"

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
    image = models.ImageField(upload_to=IMAGE_DIR, blank=True)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    updated_date = models.DateTimeField(auto_now=True)

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
    image = models.ImageField(upload_to=IMAGE_DIR, blank=True)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name

    class Meta:
        order_with_respect_to = "novel"

class Chapter(models.Model):
    name = models.CharField(max_length=512)
    volume = models.ForeignKey(Volume)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    updated_date = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

    class Meta:
        order_with_respect_to = "volume"

class ChapterContent(models.Model):
    chapter = models.OneToOneField(Chapter, related_name="content_record")
    content = models.TextField()

class HitCountRecord(models.Model):
    chapter = models.ForeignKey(Chapter, unique_for_date="date")
    date = models.DateField(auto_now_add=True)
    hits = models.IntegerField(default=1)

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    novel = models.ForeignKey(Novel)

    def __unicode__(self):
        return self.tag

