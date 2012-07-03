jQuery(function($) {
    var container = $("#chapter-content");
    var last_container_height = -1;
    var edit_box = $("#line-edit-box");
    var scroller = new AutoScroll();
    
    function get_line_obj_for_editing(o) {
        var line_obj = o.data("line_obj");
        if (!o.data("original_line_obj") && o.is(".has-original")) {
            o.data("original_line_obj", line_obj);
            line_obj = novel_importer.clone_line(line_obj, true);
            o.data("line_obj", line_obj);
        }
        return line_obj;
    }
    function refresh_selectable() {
        var new_height = container.height();
        if (new_height !== last_container_height) {
            last_container_height = new_height;
            container.selectable("refresh");
        }
    }
    function on_selection_changed() {
        var lines = [];
        var selected = container.find(".paragraph.ui-selected");
        selected.each(function() {
            lines.push($(this).data("line_obj").data);
        });
        edit_box.val(lines.join("\n")).removeClass("dirty");
        $("#fix-image-fieldset").toggle(
            selected.size() == 1 && selected.find("img.error").size() == 1
        );
    }
    function reset_elem_content(line_elem) {
        line_elem.html(line_elem.data("line_obj").data || "&nbsp;");
    }
    function get_or_create_line_elem(line_obj) {
        if (line_obj._elem) {
            return line_obj._elem;
        }
        var elem = $("<p/>").
            attr("id", line_obj.id || "").
            addClass(line_obj.type).
            data("line_obj", line_obj);

        line_obj._elem = elem;
        reset_elem_content(elem);

        return elem;
    }
    function insert_new_line(line_obj) {
        var selected = container.find(".ui-selected");
        if (selected.size() === 0) {
            return;
        }
        get_or_create_line_elem(line_obj).
            addClass("dirty new ui-selected").
            insertBefore(selected.get(0));

        refresh_selectable();
        selected.removeClass("ui-selected");
        on_selection_changed();
        update_chapter_list();
    }
    function scroll_into_view(elem) {
        var base_top = container.offset().top;
        window.scrollTo(0, elem.offset().top - base_top);
    }
    function get_chapter_name(starting_elem) {
        var name = "";
        var elem = starting_elem;
        while (elem.size() > 0 && !elem.is(".splitter")) {
            // We treat 1 or 2 consecutive lines as title, so after we find a
            // title line, look at the next line too and merge it into the title
            if (elem.is(".paragraph") && 
                !elem.is(".deleted") &&
                elem.find("img").size() === 0) {
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
                    scroll_into_view(starting_elem);
                }).appendTo(chapter_list);
        });
    }
    function merge_diff(diff) {
        $.each(diff, function(line_index, new_line_objects) {
            var line_elems = $.map(new_line_objects, function(o) {
                return get_or_create_line_elem(o)[0];
            });
            line_elems = $(line_elems);
            line_elems.addClass("new dirty");
            if (line_index < novel_importer.lines.length) {
                var existing_line = novel_importer.lines[line_index];
                var elem = existing_line._elem;
                elem.addClass("dirty deleted");
                line_elems.insertAfter(elem);
            } else {
                line_elems.appendTo(container);
            }
        });
        // Clean up diff to make it easier to read
        container.find(":not(.dirty.paragraph) + .dirty.paragraph").
            each(function() {
                var o = $(this);
                var first_insert = null;
                while (o.is(".dirty.paragraph")) {
                    var cur = o;
                    o = o.next();
                    if (cur.hasClass("new")) {
                        if (!first_insert) {
                            first_insert = cur;
                        }
                    } else {
                        if (first_insert) {
                            cur.detach().insertBefore(first_insert);
                        }
                    }
                }
            });
    }
    function commit_edit() {
        if (!edit_box.hasClass("dirty")) {
            return;
        }
        var selected = container.find(".paragraph.ui-selected");
        var lines = edit_box.val().split("\n");
        selected.each(function(i) {
            var o = $(this);
            var new_text = $.trim(i < lines.length ? lines[i] : "");
            var line_obj = get_line_obj_for_editing(o);
            if ($.trim(line_obj.data) !== new_text) {
                line_obj.data = new_text;
                o.html(new_text || "&nbsp;");
                o.addClass("dirty");
            }
        });
        edit_box.removeClass("dirty");
        update_chapter_list();
    }
    function save_locally() {
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
        refresh_selectable();
        update_chapter_list();
    }
    $("#control-panel .button").each(function() {
        $(this).button({ disabled: !!$(this).data("disabled") });
    });
    edit_box.val("").keydown(function() {
        $(this).addClass("dirty");
    }).change(function() {
        commit_edit();
    });
    $("#remove-selected").click(function() {
        container.find(".ui-selected:not(.has-original)").remove();
        container.find(".ui-selected").
            addClass("dirty deleted").
            removeClass("ui-selected");

        on_selection_changed();
        update_chapter_list();
    });
    $("#remove-all").click(function() {
        container.children().addClass("ui-selected");
        $("#remove-selected").click();
    });
    $("#new-splitter").click(function() {
        insert_new_line(novel_importer.make_splitter());
    });
    $("#new-paragraph").click(function() {
        insert_new_line(novel_importer.make_paragraph(""));
    });
    $("#save").click(function() {
        save_locally();
    });
    $("#revert-selected").click(function() {
        container.find(".ui-selected:not(.has-original)").remove();
        container.find(".ui-selected").each(function() {
            var o = $(this);
            var line_obj = o.data("original_line_obj") || o.data("line_obj");
            o.data("line_obj", line_obj);
            o.data("original_line_obj", null);
            reset_elem_content(o);
            o.removeClass("dirty deleted ui-selected");
        });
        on_selection_changed();
        update_chapter_list();
        refresh_selectable();
    });
    $("#hide-unchanged-lines, #hide-deleted-lines").change(function() {
        container.toggleClass(this.id, $(this).is(":checked"));
        refresh_selectable();
    });
    $("#do-amend").click(function() {
        var error_elem = $("#amend-error");
        error_elem.hide();
        if (container.find(".dirty").size() > 0) {
            error_elem.text("Please save or revert changed lines before amending").show();
            return;
        }
        var new_content = $.trim($("#amend-box").val());
        if (!new_content) {
            error_elem.text("Amendment is empty").show();
            return;
        }
        var diff = novel_importer.build_diff(new_content);
        merge_diff(diff);
        $("#amend-box").val("");
        update_chapter_list();
        refresh_selectable();
    });
    $("#save-volume").click(function() {
        save_locally();
        novel_importer.save_to_server();
    });
    $("#jump-to-first-invalid-image").click(function() {
        var invalid_image = container.find("img.error");
        if (invalid_image.size() > 0) {
            scroll_into_view(invalid_image);
        }
    });
    var uploader = new qq.FileUploader({
        element: $(".qq-uploader")[0],
        action: IMAGE_UPLOAD_FROM_LOCAL_URL,
        sizeLimit: 5 * 1024 * 1024,
        csrfToken: $.cookie("csrftoken"),
        onComplete: function(id, fileName, responseJSON) {
            var selected = container.find(".ui-selected");
            var line_obj = selected.data("line_obj");
            line_obj = novel_importer._(line_obj);
            line_obj.set_image_uploaded_url(
                line_obj.get_non_uploaded_images().first(), responseJSON.name
            );
            selected.html(line_obj.data).addClass("dirty");
            on_selection_changed();
        }
    });
    $(document).mousemove(function(e) {
        if (scroller.is_started()) {
            scroller.set_delta_from_mouse_event(e);
        }
    });
    novel_importer.iterate(function(i, line_obj) {
        get_or_create_line_elem(line_obj).
            addClass("has-original").
            appendTo(container);
    });
    if (novel_importer.settings.pending_diff) {
        merge_diff(novel_importer.settings.pending_diff);
        novel_importer.settings.pending_diff = null;
    }
    container.selectable({
        filter: "> p:visible",
        autoRefresh: false,
        start: function() {
            commit_edit();
            scroller.start();
        },
        stop: function() { 
            scroller.stop();
            on_selection_changed();
        }
    });
    container.find("img").load(function() {
        $(this).removeClass("error");
        refresh_selectable();
    }).error(function() {
        $(this).addClass("error");
        refresh_selectable();
        $("#jump-to-first-invalid-image").button("option", "disabled", false);
    });
    update_chapter_list();
});
