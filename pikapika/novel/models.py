from django.db import models
from django.contrib.auth.models import User

IMAGE_DIR = "images/%Y/%m/%d"

class Novel(models.Model):
    name = models.CharField(max_length=512)
    description = models.TextField()
    author = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    image = models.ImageField(upload_to=IMAGE_DIR, blank=True)
    rating_points = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

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
    chapter = models.ForeignKey(Chapter)
    date = models.DateField(auto_now_add=True)
    hits = models.IntegerField(default=1)

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    novel = models.ForeignKey(Novel)

    def __unicode__(self):
        return self.tag

