jQuery(function($) {
    var container = $("#chapter-content");
    var edit_box = $("#line-edit-box");
    $("#control-panel .button").button();
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
    function create_line_elem(line_obj) {
        return $("<p/>").
            attr("id", line_obj.id || "").
            addClass(line_obj.type).
            data("line_obj", line_obj).
            html(line_obj.data || "&nbsp;");
    }
    function insert_new_line(line_obj) {
        var selected = container.find(".ui-selected");
        if (selected.size() === 0) {
            return;
        }
        create_line_elem(line_obj).
            addClass("dirty new").
            insertBefore(selected.get(0));

        container.selectable("refresh");
    }
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
    });
    $("#remove-selected").click(function() {
        container.find(".ui-selected:not(.has-original)").remove();
        container.find(".ui-selected").
            addClass("dirty deleted").
            removeClass("ui-selected").
            selectable("refresh");

        container.selectable("refresh");
        on_selection_changed();
    });
    $("#new-splitter").click(function() {
        insert_new_line({type: "splitter"});
    });
    $("#new-paragraph").click(function() {
        insert_new_line({type: "paragraph", data: ""});
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
        create_line_elem(line_obj).addClass("has-original").appendTo(container);
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
});
