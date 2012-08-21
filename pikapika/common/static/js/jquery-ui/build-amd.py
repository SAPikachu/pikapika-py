#!/usr/bin/env python

import os
import re
import json

BASE_DIR = "../../../../../submodules/jquery-ui/ui"

def convert_file_name(name):
    return (
        os.path.splitext(name)[0]
            .replace("jquery.ui.", "")
            .replace("jquery.", "")
            .replace(".", "-")
        + ".js"
    )

def build_file(path_parts):
    dependencies = ["jquery"]
    if "ui.core." not in path_parts[-1]:
        dependencies.append("./core")

    content = ""
    in_header = True

    with open(os.path.join(*([BASE_DIR] + path_parts)), "r") as f:
        for line in f:
            if in_header:
                m = re.match(r"\s*\*\s*(?P<file_name>[\w.]+\.js)", line, re.I)
                if m:
                    file_name = convert_file_name(m.group("file_name"))
                    module_name = "./" + file_name[:-3]
                    if module_name not in dependencies:
                        dependencies.append(module_name)

            elif "*/" in line:
                in_header = False

            content += line
    
    content = "define({}, function(jQuery) {{\n{}\n}});".format(
        json.dumps(dependencies), content,
    )

    if len(path_parts) > 1:
        parent = os.path.join(*path_parts[:-1])
        if not os.path.isdir(parent):
            os.makedirs(parent)

    with open(convert_file_name(os.path.join(*path_parts)), "w") as f:
        f.write(content)

def build(subdir_parts=None):
    subdir_parts = subdir_parts or []

    current_dir = os.path.join(*([BASE_DIR] + subdir_parts))
    for item in os.listdir(current_dir):
        if os.path.isdir(os.path.join(current_dir, item)):
            build(subdir_parts + [item])
        else:
            build_file(subdir_parts + [item])

if __name__ == "__main__":
    build()

