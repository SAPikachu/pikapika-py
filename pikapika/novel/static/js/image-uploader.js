(function($) {
    $.fn.imageUploader = function(target_elem, url_upload, url_from_external, image_root) {
        return this.each(function() {
            var o = $(this);
            var preview_div = o.find(".preview");
            var cookie_box = o.find(".external-cookies");

            // Don't let buttons submit the page
            o.find("input[type=submit]").click(function(e) { 
                e.preventDefault(); 
            });
            preview_div.find("img").load(function() {
                preview_div.find(".qq-upload-spinner").hide();
                $(this).show();
            }).error(function() {
                preview_div.find(".qq-upload-spinner").hide();
            }).click(function() {
                window.open(this.src);
            });
            target_elem.change(function() {
                preview_div.find(".qq-upload-spinner").show();
                preview_div.find("img").hide().
                    attr("src", image_root + $(this).val());
            }).change();
            cookie_box.val($.jStorage.get("downloader-cookies", ""));
            cookie_box.change(function() {
                $.jStorage.set("downloader-cookies", $(this).val());
            });

            var uploader = new qq.FileUploader({
                element: this,
                action: url_upload,
                sizeLimit: 5 * 1024 * 1024,
                template: null,
                csrfToken: $.cookie("csrftoken"),
                onComplete: function(id, fileName, responseJSON) {
                    target_elem.val(responseJSON.name).change();
                }
            });
            o.find(".download-button").click(function() {
                var url = $.trim(o.find(".external-url").val());
                if (!url) {
                    return;
                }
                var button = $(this);
                button.attr("disabled", "disabled");
                var list_item = $(uploader._options.fileTemplate);
                list_item.find(".qq-upload-file").text(url);
                list_item.find(".qq-upload-cancel").remove();
                list_item.appendTo(o.find(".qq-upload-list"));
                $.ajax({
                    type: "POST",
                    url: url_from_external,
                    data: {
                        url: url,
                        cookies: cookie_box.val()
                    },
                    dataType: "json",
                    success: function(data) {
                        target_elem.val(data.name).change();
                        list_item.addClass("qq-upload-success");
                    },
                    error: function(xhr, textStatus, errorThrown) {
                        var content_type = xhr.getResponseHeader("Content-Type").toLowerCase();
                        if (content_type.indexOf("application/json") === 0) {
                            var resp = $.parseJSON(xhr.responseText);
                            list_item.find(".qq-upload-failed-text").text(
                                "Failed (" + resp.message + ")"
                            );
                        }
                        list_item.addClass("qq-upload-fail");
                    },
                    complete: function() {
                        button.removeAttr("disabled");
                        list_item.find(".qq-upload-spinner").remove();
                    }
                });
            });
        });
    };
})(jQuery);
