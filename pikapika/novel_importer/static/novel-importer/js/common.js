// Requires jQuery, jStorage
(function($) {

    window.novel_importer = {
        _id_counter: 0,
        id_prefix: "chap-",
        load: function() {
            this.lines = $.jStorage.get("novel-importer-lines", []);
            this.settings = $.jStorage.get("novel-importer-settings", {});
        },
        save: function() {
            $.jStorage.set("novel-importer-lines", this.lines);
            $.jStorage.set("novel-importer-settings", this.settings);
        },
        clear: function() {
            this.lines = [];
        },
        add_paragraph: function(content, id, pos) {
            this.add_line({
                type: "paragraph",
                id: id || this.generate_paragraph_id(),
                data: content
            }, pos);
        },
        add_chapter_splitter: function(pos) {
            this.add_line({
                type: "splitter"
            }, pos);
        },
        add_line: function(line_obj, pos) {
            if (typeof pos === "undefined") {
                pos = this.lines.length;
            }
            this.lines.splice(pos, 0, line_obj);
        },
        remove_line: function(line_obj_or_pos) {
            if (typeof line_obj_or_pos !== "number") {
                line_obj_or_pos = this.lines.indexOf(line_obj_or_pos);
            }
            this.lines.splice(line_obj_or_pos, 1);
        },
        iterate: function(callback, num_chapters_to_skip) {
            num_chapters_to_skip = num_chapters_to_skip || 0;
            $.each(this.lines, function(i, line_obj) {
                if (num_chapters_to_skip > 0) {
                    if (line_obj.type == "splitter") {
                        num_chapters_to_skip--;
                    }
                    return;
                }
                return callback.apply(this, arguments);
            });
        },
        generate_paragraph_id: function() {
            this._id_counter++;
            return this.id_prefix + 
                (new Date().getTime()) + 
                "-" + 
                this._id_counter;
        },
        __placeholder: null
    };

    novel_importer.load();

})(jQuery);
