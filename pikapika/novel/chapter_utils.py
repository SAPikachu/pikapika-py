from __future__ import print_function, unicode_literals

from time import time

MEDIA_URL_PREFIX = "_MEDIA_URL_"

def timestamp():
    return int(time() * 1000)

class ChapterIdGenerator(object):
    def __init__(self, prefix="chap-"):
        self.counter = 0
        self.prefix = prefix

    def __call__(self):
        self.counter += 1
        return "{}{}-{}".format(self.prefix, timestamp(), self.counter)

def make_line(data, line_id=None, tags=None):
    return {
        "id": line_id or "chap-{}-{}".format(timestamp(), id(data)),
        "type": "paragraph",
        "tags": tags or [],
        "data": data,
    }

def elem_to_unicode(elem):
    if isinstance(elem, unicode):
        # NavigatableString
        return elem.output_ready(formatter="html")
    else:
        return elem.decode(formatter="html")

def parse_html(html, id_generator=None):
    """
    Parses properly rendered chapter into line objects
    """
    # We won't do parsing often, so only import BS when needed
    from bs4 import BeautifulSoup
    soup = BeautifulSoup("<html><body>{}</body></html>".format(html))
    lines = []
    ALLOWED_ELEMENTS = ("p", "table")
    _generate_id = id_generator or ChapterIdGenerator()
    for elem in soup.select("body")[0].find_all(True, recursive=False):
        if elem.name not in ALLOWED_ELEMENTS:
            import pdb
            pdb.set_trace()

        assert elem.name in ALLOWED_ELEMENTS
        id = elem.get("id") or _generate_id()
        if elem.name != "p":
            # This element should be output as-is, wrap it into a div so that
            # codes below doesn't need to do a special check
            elem = elem.wrap(soup.new_tag("div"))

        for link in elem.find_all("a"):
            children = link.find_all(True, recursive=False)
            if len(children) == 1 and children[0].name == "img":
                img_url = link["href"]
                if "://" not in img_url:
                    new_img = soup.new_tag("img")
                    if MEDIA_URL_PREFIX not in img_url:
                        img_url = MEDIA_URL_PREFIX + img_url.lstrip("/")

                    new_img["src"] = img_url
                    link.replace_with(new_img)

        lines.append(make_line(
            line_id=id,
            data="".join([elem_to_unicode(x) for x in elem.contents]),
        ))

    return lines

def insert_hidden_title(lines, title):
    """
    Inserts a hidden line containing the title into content, so that chapter 
    editor can use that.
    """

    lines.insert(0, make_line(title, tags=["hidden"]))
    # Need another empty line to separate the title from actual content
    lines.insert(1, make_line("", tags=["hidden"]))


def render(chapter_lines):
    raise NotImplementedError()

