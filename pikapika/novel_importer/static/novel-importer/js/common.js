// Requires jQuery, jStorage
(function($) {
    var line_object_keys = ["id", "type", "data"];
    var MEDIA_URL_PREFIX = "_MEDIA_URL_";
    function Line(raw_line) {
        $.extend(this, raw_line);
    }
    $.extend(Line.prototype, {
        _has_line_prototype: true,
        _get_elem: function() {
            if (this.type !== "paragraph") {
                throw "Can only create element for paragraph";
            }
            if (!this.__internal_elem) {
                this.__internal_elem = $("<div/>").html(this._safe_data());
            }
            return this.__internal_elem;
        },
        _sync_from_elem: function() {
            this.data = this._get_elem().html();
        },
        _safe_data: function() {
            return this.data || "";
        },
        get_images: function() {
            if (this._safe_data().indexOf("img") === -1) {
                return $();
            }
            return this._get_elem().find("img");
        },
        get_non_uploaded_images: function() {
            return this.get_images().filter(function() {
                return $(this).attr("src").indexOf(MEDIA_URL_PREFIX) === -1;
            });
        },
        set_image_uploaded_url: function(img_elem, returned_url) {
            var old_src = img_elem.attr("src");
            if (old_src.indexOf(MEDIA_URL_PREFIX) === -1) {
                img_elem.attr("data-original-src", old_src);
            }
            img_elem.attr("src", MEDIA_URL_PREFIX + returned_url);
            this._sync_from_elem();
        },
        clone: function(with_extra_properties) {
            var line_obj = this;
            if (with_extra_properties) {
                return new Line($.extend({}, line_obj));
            }
            var result = new Line({});
            $.each(line_object_keys, function(i, key) {
                if (line_obj[key] !== undefined) {
                    result[key] = line_obj[key];
                }
            });
            return result;
        }
    });

    window.novel_importer = {
        _id_counter: 0,
        id_prefix: "chap-",
        load: function() {
            this.lines = $.jStorage.get("novel-importer-lines", []);
            this.settings = $.jStorage.get("novel-importer-settings", {});
        },
        save: function() {
            var self = this;
            var lines_to_be_saved = $.map(this.lines, function(line) {
                return self.clone_line(line, false);
            });
            $.jStorage.set("novel-importer-lines", lines_to_be_saved);

            $.jStorage.set("novel-importer-settings", this.settings);
        },
        clear: function() {
            this.lines = [];
        },
        _: function(line_obj) {
            if (line_obj instanceof Line || line_obj._has_line_prototype) {
                return line_obj;
            }
            line_obj.__proto__ = Line.prototype;
            return line_obj;
        },
        clone_line: function(line_obj, with_extra_properties) {
            var wrapped = this._(line_obj);
            return wrapped.clone(with_extra_properties);
        },
        make_paragraph: function(content, id) {
            return {
                type: "paragraph",
                id: id || this.generate_paragraph_id(),
                data: content
            };
        },
        make_splitter: function() {
            return { type: "splitter" };
        },
        add_paragraph: function(content, id, pos) {
            this.add_line(this.make_paragraph(content, id), pos);
        },
        add_chapter_splitter: function(pos) {
            this.add_line(this.make_splitter(), pos);
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
