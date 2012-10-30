(function($) {
    novel_importer.handle_content = function(content, site_cookies) {
        /* Format of content: 
        * [
        *   [
        *       "Paragraph 1 of chapter 1", 
        *       "Paragraph 2 of chapter 1", 
        *       ...
        *   ],
        *   [
        *       "Paragraph 1 of chapter 2", 
        *       "Paragraph 2 of chapter 2", 
        *       ...
        *   ],
        *   ...
        * ]
        */
        var self = this;

        var complete_import = function() {
            self.settings.site_cookies = site_cookies;
            self.save();
            location.href = "editor";
        };

        var append_content = function() {
            $.each(content, function(i, chapter) {
                if (self.lines.length > 0) {
                    self.add_chapter_splitter();
                }
                $.each(chapter, function(_, paragraph) {
                    self.add_paragraph(paragraph);
                });
            });
            complete_import();
        };

        var merge_content = function() {
            var diff = novel_importer.build_diff(content);
            self.settings.pending_diff = diff;
            complete_import();
        };

        var replace_content = function() {
            self.clear();
            append_content();
        };

        if (this.lines.length > 0) {
            $("#import-mode-merge").data("handler", merge_content);
            $("#import-mode-append").data("handler", append_content);
            $("#import-mode-replace").data("handler", replace_content);
            $("#do-import").click(function(e) {
                e.preventDefault();
                $("#mode-select input:checked").data("handler")();
            });
            $("#mode-select").show();
        } else {
            append_content();
        }
    };
})(jQuery);
