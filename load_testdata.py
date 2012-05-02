#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import json

from django.contrib.auth.models import User

from pikapika.novel.models import *

DATA_FILE = "testdata/pikapika.json"

USER_ID = 1

FIELD_MAPPINGS = {
    "Novel": {
        "Name": "name",
        "Description": "description",
        "Author": "author",
        "Publisher": "publisher",
    },
    "Volume": {
        "Name": "name",
        "Description": "description",
    },
    "Chapter": {
        "Name": "name",
    },
    # TODO: Add remaining fields
}

def fill_model(model, values):
    mapping = FIELD_MAPPINGS[model.__class__.__name__]
    for source, dest in mapping.items():
        setattr(model, dest, values[source])

def get_source_sort_key(source):
    return (source["SortIndex"], source["Id"])

def add_novel(values):
    print("Loading", values["Name"])
    user = User.objects.get(pk=USER_ID)
    novel = Novel()
    fill_model(novel, values)
    novel.save()
    for volume_values in sorted(values["Volumes"], key=get_source_sort_key):

        volume = Volume(novel=novel)
        fill_model(volume, volume_values)
        volume.save()
        for chapter_values in \
            sorted(volume_values["Chapters"], key=get_source_sort_key):

            chapter = Chapter(volume=volume, posted_by=user)
            fill_model(chapter, chapter_values)
            chapter.save()
            r = HitCountRecord(chapter=chapter, hits=chapter_values["HitCount"])
            r.save()

def load_testdata():
    with open(DATA_FILE, "r") as f:
        all_novels = json.load(f)

    add_novel(all_novels[0])
    add_novel(all_novels[1])

if __name__ == "__main__":
    load_testdata()

