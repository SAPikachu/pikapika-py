from __future__ import print_function, unicode_literals

def first(list, **kwargs):
    if len(list) == 0 and "default" in kwargs:
        return kwargs["default"]

    return list[0] 
