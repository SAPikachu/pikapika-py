jQuery(function($) {
    var container = $("#chapter-content");
    var edit_box = $("#line-edit-box");
    
    function get_line_obj_for_editing(o) {
        var line_obj = o.data("line_obj");
        if (!o.data("original_line_obj") && o.is(".has-original")) {
            o.data("original_line_obj", line_obj);
            line_obj = $.extend(true, {}, line_obj);
            o.data("line_obj", line_obj);
            o.addClass("dirty");
        }
        return line_obj;
    }
    function on_selection_changed() {
        var lines = [];
        container.find(".paragraph.ui-selected").each(function() {
            lines.push($(this).data("line_obj").data);
        });
        edit_box.val(lines.join("\n")).removeClass("dirty");
    }
    function get_or_create_line_elem(line_obj) {
        if (line_obj._elem) {
            return line_obj._elem;
        }
        var elem = $("<p/>").
            attr("id", line_obj.id || "").
            addClass(line_obj.type).
            data("line_obj", line_obj).
            html(line_obj.data || "&nbsp;");

        line_obj._elem = elem;
        return elem;
    }
    function insert_new_line(line_obj) {
        var selected = container.find(".ui-selected");
        if (selected.size() === 0) {
            return;
        }
        get_or_create_line_elem(line_obj).
            addClass("dirty new").
            insertBefore(selected.get(0));

        container.selectable("refresh");
        update_chapter_list();
    }
    function get_chapter_name(starting_elem) {
        var name = "";
        var elem = starting_elem;
        while (elem.size() > 0 && !elem.is(".splitter")) {
            // We treat 1 or 2 consecutive lines as title, so after we find a
            // title line, look at the next line too and merge it into the title
            if (elem.is(".paragraph") && elem.find("img").size() === 0) {
                var should_break = !!name;
                var line = $.trim(elem.text().replace(/\s+/, " "));
                if (line) {
                    if (name) {
                        name += " ";
                    }
                    name += line;
                    elem.addClass("chapter-name");
                }
                if (should_break) {
                    break;
                }
            }
            elem = elem.next();
        }
        return name;
    }
    function iterate_chapters(callback) {
        var elem = container.children().eq(0);
        while (elem.size() > 0) {
            var chapter_name = get_chapter_name(elem);
            var next_splitter = elem.nextAll(".splitter").eq(0);
            if (chapter_name) {
                callback(chapter_name, elem, function() {
                    return elem.nextUntil(next_splitter).
                        andSelf().
                        filter(".paragraph:not(.chapter-name)");
                });
            }
            elem = next_splitter.next();
        }
        container.find("chapter-name").removeClass("chapter-name");
    }
    function update_chapter_list() {
        var chapter_list = $("#chapter-list");
        chapter_list.children().remove();
        iterate_chapters(function(chapter_name, starting_elem, content_getter) {
            $("<li/>").text(chapter_name).
                click(function() {
                    var base_top = $("#chapter-content").offset().top;
                    window.scrollTo(
                        0, starting_elem.offset().top - base_top
                    );
                }).appendTo(chapter_list);
        });
    }
    $("#control-panel .button").button();
    edit_box.val("").keydown(function() {
        $(this).addClass("dirty");
    }).change(function() {
        var selected = container.find(".paragraph.ui-selected");
        var lines = edit_box.val().split("\n");
        selected.each(function(i) {
            var o = $(this);
            var new_text = $.trim(i < lines.length ? lines[i] : "");
            var line_obj = get_line_obj_for_editing(o);
            line_obj.data = new_text;
            o.html(new_text || "&nbsp;");
        });
        edit_box.removeClass("dirty");
        update_chapter_list();
    });
    $("#remove-selected").click(function() {
        container.find(".ui-selected:not(.has-original)").remove();
        container.find(".ui-selected").
            addClass("dirty deleted").
            removeClass("ui-selected").
            selectable("refresh");

        container.selectable("refresh");
        on_selection_changed();
        update_chapter_list();
    });
    $("#new-splitter").click(function() {
        insert_new_line(novel_importer.make_splitter());
    });
    $("#new-paragraph").click(function() {
        insert_new_line(novel_importer.make_paragraph(""));
    });
    $("#save").click(function() {
        container.find(".deleted").remove();
        novel_importer.clear();
        container.children("p").each(function() {
            var o = $(this);
            var line_obj = o.data("line_obj");
            if (line_obj.type === "paragraph" && !line_obj.id) {
                line_obj.id = novel_importer.generate_paragraph_id();
            }
            novel_importer.add_line(line_obj);
            o.addClass("has-original").removeClass("new dirty");
            o.data("original_line_obj", null);
        });
        novel_importer.save();
    });
    novel_importer.iterate(function(i, line_obj) {
        get_or_create_line_elem(line_obj).
            addClass("has-original").
            appendTo(container);
    });
    container.selectable({
        filter: "> p:not(.deleted)",
        autoRefresh: false,
        stop: on_selection_changed
    });
    container.find("img").load(function() {
        container.selectable("refresh");
    }).error(function() {
        container.selectable("refresh");
    });
    update_chapter_list();
});
