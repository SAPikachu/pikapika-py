(function($) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
            return typeof args[number] != 'undefined'
            ? args[number]
            : match
            ;
        });
    };

    function show_message(message) {
        return $("<li/>").text(message).appendTo($("#messages"));
    }
    function show_error(message) {
        return show_message(message).addClass("error");
    }
    function upload_images(success_callback) {
        var pending_images = [];
        novel_importer.iterate(function(i, line_obj) {
            if (line_obj.type !== "paragraph") {
                return;
            }
            line_obj = novel_importer._(line_obj);
            line_obj.get_non_uploaded_images().each(function() {
                var o = $(this);
                pending_images.push({
                    line_obj: line_obj,
                    img_elem: o
                });
            });
        });
        var total_images = pending_images.length;

        var upload_next = function() {
            if (pending_images.length === 0) {
                success_callback();
                return;
            }
            var current_item = pending_images.shift();
            var url = current_item.img_elem.attr("src");
            var index = total_images - pending_images.length;

            var attempt_num = 0;
            function do_upload() {
                var upload_text = 
                    "Uploading {0} ({1}/{2}), attempt #{3}".format(
                        url, index, total_images, attempt_num
                    );

                show_message(upload_text);
                var target_url = url;
                if (attempt_num % 2 === 1) {
                    // Try Google image proxy
                    target_url = "https://images2-focus-opensocial.googleusercontent.com/gadgets/proxy?url={0}&container=focus&gadget=a&no_expand=1&resize_h=0&rewriteMime=image%2F*".format(encodeURIComponent(url));
                }
                $.ajax({
                    type: "POST",
                    url: IMAGE_UPLOAD_URL,
                    data: {
                        url: target_url,
                        cookies: novel_importer.settings.site_cookies
                    },
                    dataType: "json",
                    success: function(resp) {
                        current_item.line_obj.set_image_uploaded_url(
                            current_item.img_elem, resp.name
                        );
                        novel_importer.save();
                        upload_next();
                    },
                    error: function(jqxhr, text_status, error_thrown) {
                        var message = null;
                        var status_code = jqxhr.status;
                        try
                        {
                            var resp = $.parseJSON(jqxhr.responseText);
                            message = resp.message;
                            if (resp.code) {
                                status_code = resp.code;
                            }
                        } catch (e) {
                        }
                        message = message ||
                            "{0}, {1}".format(text_status, error_thrown);

                        if (status_code >= 502 && status_code <= 504) {
                            attempt_num++;
                            upload_text += " (Failed, waiting for retry...)";
                            show_message(upload_text);
                            setTimeout(
                                do_upload, 
                                Math.pow(2, attempt_num) * 1000
                            );
                        } else {
                            show_error("Error while uploading {0} ({1})".format(
                                url, message
                            ));
                        }
                    }
                });
            }
            do_upload();
        };
        upload_next();
    }
    function upload_volume() {
        var volume_id = novel_importer.settings.volume_id;
        if (!volume_id) {
            show_error("You have not selected a volume");
            return;
        }
        function new_chapter() {
            return {
                name: "",
                lines: []
            };
        }
        var current_chapter = new_chapter();
        var got_name = false;
        var in_prologue = true;
        var chapters = [current_chapter];
        novel_importer.iterate(function(i, line_obj) {
            if (line_obj.type === "splitter") {
                got_name = false;
                in_prologue = true;
                current_chapter = new_chapter();
                chapters.push(current_chapter);
                return;
            }
            line_obj.tags = [];
            var cleaned_line = line_obj.data || "";
            cleaned_line = cleaned_line.replace(/(&nbsp;|\s)+/gi, " ");
            cleaned_line = $.trim(cleaned_line);
            if (!got_name) {
                var have_first_line = !!current_chapter.name;
                if (novel_importer._(line_obj).get_images().size() === 0) {
                    line_obj.tags.push("hidden");
                    if (cleaned_line) {
                        if (current_chapter.name) {
                            current_chapter.name += " ";
                        }
                        current_chapter.name += cleaned_line;
                    }
                }
                got_name = have_first_line;
            } else if (in_prologue) {
                if (!cleaned_line) {
                    line_obj.tags.push("hidden");
                } else {
                    in_prologue = false;
                }
            }
            current_chapter.lines.push(line_obj);
        });
        // Filter out empty chapters
        chapters = $.map(chapters, function(chapter) {
            if (!chapter.name) {
                return null;
            }
            for (var i = 0; i < chapter.lines.length; i++) {
                var tags = chapter.lines[i].tags || [];
                if (tags.indexOf("hidden") === -1) {
                    return chapter;
                }
            }
            return null;
        });
        $.ajax({
            type: "POST",
            url: "save-ajax",
            data: {
                volume_id: volume_id,
                chapters_json: JSON.stringify(chapters)
            },
            dataType: "json",
            success: function(data) {
                show_message("Success!");
                novel_importer.reset();
                location.href = data.return_url;
            },
            error: function(jqxhr, status, errorThrown) {
                var message;
                try 
                {
                    message = $.parseJSON(jqxhr.responseText).message;
                } catch (e) {
                    message = "Unexpected error ({0}, {1})".format(
                        status, errorThrown
                    );
                }
                show_error("Unable to upload volume: " + message);
            }
        });
    }
    novel_importer.save_to_server = function() {
        upload_images(function() {
            upload_volume();
        });
    };
    $(function() {
        novel_importer.save_to_server();
    });
})(jQuery);
