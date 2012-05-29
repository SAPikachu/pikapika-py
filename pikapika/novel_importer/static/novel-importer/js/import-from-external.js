(function($) {
    novel_importer.handle_content = function(content, site_cookies) {
        // TODO: Handle existing content
        this.clear();
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
        $.each(content, function(i, chapter) {
            if (i > 0) {
                self.add_chapter_splitter();
            }
            $.each(chapter, function(_, paragraph) {
                self.add_paragraph(paragraph);
            });
        });
        this.settings.site_cookies = site_cookies;
        this.save();
        location.href = "editor";
    };
})(jQuery);
