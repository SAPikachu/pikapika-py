from __future__ import print_function, unicode_literals

import os
from glob import glob
import sys
import hashlib

from django.core.management.base import NoArgsCommand
from django.conf import settings

STATIC_PATTERNS = (
    "pikapika/common/static/js/*.js",
    "pikapika/novel/static/css/screen.css",
)
ROOT = settings.PROJECT_ROOT
OUTPUT = os.path.join(ROOT, "pikapika/novel/static_version.py")

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        hasher = hashlib.sha1()
        for pattern in STATIC_PATTERNS:
            files = glob(os.path.join(ROOT, pattern))
            if not files:
                print("Warning: Can't find any file for pattern " + pattern,
                      file=sys.stderr)

            files.sort()
            for file_name in files:
                with open(file_name, "rb") as f:
                    hasher.update(f.read())

        version = hasher.hexdigest()[:8]
        with open(OUTPUT, "w") as f:
            f.write("""STATIC_VERSION = "{}"\n""".format(version))
