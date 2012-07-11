(function($) {
    novel_importer.begin_edit = function(volume_id, chapters) {
        novel_importer.settings.volume_id = volume_id;
        if (novel_importer.lines.length == 0) {
            $.each(chapters, function() {
                $.each(this.lines, function() {
                    novel_importer.add_line(this);
                });
                novel_importer.add_chapter_splitter();
            });
        }
        novel_importer.save();
        location.href = "editor";
    };
})(jQuery);
