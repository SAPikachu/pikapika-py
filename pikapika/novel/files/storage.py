from __future__ import print_function, unicode_literals

import os

from django.core.files.storage import FileSystemStorage
from django.core.files.move import _samefile

class CustomFileSystemStorage(FileSystemStorage):
    """
    Don't duplicate the file if content points to a file in media directory
    that appears to be the same.
    """
    def save(self, name, content):
        if name is None:
            name = content.name

        full_name = self.path(name)
        full_name_content = self.path(content.name)

        # Ensure that two pathes really point to the same file
        if (_samefile(full_name, full_name_content) and 
            os.path.isfile(full_name) and
            os.stat(full_name).st_size == content.size):

            return name
        else:
            return super(CustomFileSystemStorage, self).save(name, content)
