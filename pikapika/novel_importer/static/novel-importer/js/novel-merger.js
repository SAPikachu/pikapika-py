(function($) {
    var SER_LINE_START = "@!@!@!";
    var SER_FIELD_SPLITTER = "@-@-@-";

    var dmp = new diff_match_patch();
    dmp.Diff_Timeout = 50.0;
    dmp.Diff_EditCost = 0;

    var serialize_line = function(i, line_obj) {
        return ["{", i, "}", line_obj.data || ""].join("");
        return [
            SER_LINE_START, line_obj.type,
            SER_FIELD_SPLITTER, line_obj.id || "",
            SER_FIELD_SPLITTER, line_obj.data || ""
        ].join("");
    };

    var get_text_for_diff = function(num_chapters_to_skip) {
        var converted_lines = [];
        novel_importer.iterate(function(i, line_obj) {
            converted_lines.push(serialize_line(i, line_obj));
        }, num_chapters_to_skip);
        return converted_lines.join("\n");
    };

    var sanitize_content = function(content) {
        if ($.isArray(content)) {
            // Content is from extractor script, flatten it
            var flattened = [];
            $.each(content, function(_, chapter) {
                $.each(chapter, function(_, paragraph) {
                    flattened.push(paragraph);
                });
                flattened.push("");
            });
            content = flattened.join("\n");
        }
        // Trim all lines
        content = content.replace(/^(?:&nbsp;|\s)*(.*)(?:&nbsp;|\s)*$/gm, "$1");
        // Collapse multiple empty lines
        content = content.replace(/\n\n+/g, "\n\n");
        return content;
    };

    var compute_diff = function(old_text, new_text) {
        // TODO
    };

    novel_importer.merge_content = function(new_content) {
        var old_content = get_text_for_diff();
        var sanitized_new_content = sanitize_content(new_content);

        var diff = compute_diff(old_content, sanitized_new_content);
        // TODO
    };
})(jQuery);
