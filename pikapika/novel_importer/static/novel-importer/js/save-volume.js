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
    }
    function upload_images() {
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

        var upload_next = function(success_callback) {
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
