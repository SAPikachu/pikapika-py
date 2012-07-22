#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import json
import warnings
import os

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction

from pikapika.novel.models import *

DATA_FILE = "testdata/pikapika.json"
USER_ID = 1
IMAGE_BASE = "/mnt/exchange"

FIELD_MAPPINGS = {
    "Novel": {
        "Id": "pk",
        "Name": "name",
        "Description": "description",
        "Author": "author",
        "Publisher": "publisher",

        # ImageUrl -> image
        # UpdatedDate -> updated_date
    },
    "Volume": {
        "Id": "pk",
        "Name": "name",
        "Description": "description",
        # ImageUrl -> image
    },
    "Chapter": {
        "Id": "pk",
        "Name": "name",
        # UpdatedDate -> updated_date
    },
    # TODO: Add remaining fields
}

def fill_model(model, values):
    mapping = FIELD_MAPPINGS[model.__class__.__name__]
    for source, dest in mapping.items():
        setattr(model, dest, values[source] or "")

def get_source_sort_key(source):
    return (source["SortIndex"], source["Id"])

def set_updated_date(model, date):
    with warnings.catch_warnings():
        # Suppress warnings about naive datetime
        warnings.simplefilter("ignore")
        model.__class__.objects.filter(pk=model.pk).update(updated_date=date)

def set_image(model, old_path):
    if not old_path:
        return

    model.image = ContentFile(
        open(os.path.join(IMAGE_BASE, old_path.strip("/")), "rb").read(),
        name=os.path.basename(old_path),
    )

def add_novel(values):
    print("Loading", values["Name"])
    user = User.objects.get(pk=USER_ID)
    novel = Novel()
    novel.pk = values["Id"] + 100
    fill_model(novel, values)
    set_image(novel, values["ImageUrl"])
    novel.save()
    set_updated_date(novel, values["UpdatedDate"])

    for volume_values in sorted(values["Volumes"], key=get_source_sort_key):

        volume = Volume(novel=novel)
        fill_model(volume, volume_values)
        set_image(volume, volume_values["ImageUrl"])
        volume.save()
        for chapter_values in \
            sorted(volume_values["Chapters"], key=get_source_sort_key):

            chapter = Chapter(volume=volume, posted_by=user)
            fill_model(chapter, chapter_values)
            chapter.save()
            set_updated_date(chapter, chapter_values["UpdatedDate"])

            r = HitCountRecord(chapter=chapter, hits=chapter_values["HitCount"])
            r.save()

@transaction.commit_on_success
def load_testdata():
    with open(DATA_FILE, "r") as f:
        all_novels = json.load(f)

    [add_novel(x) for x in all_novels]

if __name__ == "__main__":
    load_testdata()

