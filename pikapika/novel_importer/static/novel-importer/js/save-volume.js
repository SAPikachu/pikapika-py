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

    var URL_PREFIX = "_MEDIA_URL_";
    var dialog;
    function show_message(message) {
        dialog.find(".message").text(message);
    }
    function show_error(message) {
        show_message(message);
        dialog.dialog("option", "buttons", {
            "OK": function() {
                location.reload();
            }
        });
    }
    function upload_images() {
        var pending_images = [];
        novel_importer.iterate(function(i, line_obj) {
            if (line_obj.type !== "paragraph") {
                return;
            }
            var content = line_obj.data || "";
            if (content.indexOf("img") === -1) {
                return;
            }
            var elem = $("<div/>").html(line_obj.data);
            elem.find("img").each(function() {
                var o = $(this);
                if (o.attr("src").indexOf(URL_PREFIX) !== -1) {
                    return;
                }
                pending_images.push({
                    line_obj: line_obj,
                    line_elem: elem,
                    img_elem: o
                });
            });
        });
        var total_images = pending_images.length;

        var upload_next = function(success_callback) {
            if (pending_images.length === 0) {
                success_callback();
                return;
            }
            var current_item = pending_images.shift();
            var url = current_item.img_elem.attr("src");
            var index = total_images - pending_images.length;
            show_message(
                "Uploading {0} ({1}/{2})".format(url, index, total_images)
            );
            $.ajax({
                type: "POST",
                url: IMAGE_UPLOAD_URL,
                data: {
                    url: url,
                    cookies: novel_importer.settings.site_cookies
                },
                dataType: "json",
                success: function(resp) {
                    current_item.img_elem.attr("data-original-src", url);
                    current_item.img_elem.attr(
                        "src", URL_PREFIX + resp.name
                    );
                    current_item.line_obj.data = current_item.line_elem.html();
                    novel_importer.save();
                    upload_next();
                },
                error: function(jqxhr, text_status, error_thrown) {
                    show_error("Error while uploading {0} ({1}, {2})".format(
                        url, text_status, error_thrown
                    ));
                }
            });
        };
        upload_next();
    }
    novel_importer.save_to_server = function() {
        dialog = $("<div/>").
            attr("title", "Processing...").
            append($("<div class='message'></div>")).
            dialog({
                closeOnEscape: false,
                draggable: false,
                modal: true,
                resizable: false,
                width: 600,

                beforeClose: function() { return false; }
            });

        upload_images(function() {
            show_message("Success");
        });
    };
})(jQuery);
