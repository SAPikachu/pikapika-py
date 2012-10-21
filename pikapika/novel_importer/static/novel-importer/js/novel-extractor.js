// This script is intended to be inserted to pages by bookmarklet
(function() {
    var node = document.createElement("script");
    node.src = "http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js";
    node.onload = function() {
        var CONTENT_ELEM_SELECTOR = "td[id^=postmessage_], span.tpc_content";
        var CONTENT_THRESHOLD = 10;

        function has_content(elem) {
            var text = elem.text();
            var re = /[\uFF0C\u3002]/g // /[，。]/g;
            var sentence_count = 0;
            while (re.exec(text)) {
                sentence_count++;
                if (sentence_count >= CONTENT_THRESHOLD) {
                    return true;
                }
            }
            return false;
        }
        function is_content_elem(elem) {
            var prev_result = elem.data("is_content_elem");
            if ((typeof prev_result) === "boolean") {
                return prev_result;
            }
            var result = false;
            var sub_contents = 
                elem.find(CONTENT_ELEM_SELECTOR).filter(function() {
                    return is_content_elem($(this));
                });

            if (sub_contents.size() == 0) {
                result = has_content(elem);
            }
            elem.data("is_content_elem", result);
            return result;
        }

        function preprocess_elem() {
            elem = this;
            if (elem.className && 
                elem.tagName !== "TABLE" && 
                elem.tagName !== "TD" && 
                elem.tagName !== "IMG") {

                $(elem).remove();
                return;
            }
            if (elem.tagName == "DIV") {
                $(elem).remove();
                return;
            }
            $(elem).children().each(preprocess_elem);
        }

        function normalize_css_value(value) {
            return (value + "").toLowerCase().replace(/\s/g, "");
        }

        function build_content(elem) {
            elem = $(elem);
            var paragraphs = [];
            var current_paragraph = "";
            var default_style = {
                "font-style": ["normal"],
                "text-decoration": ["none"],
                "font-weight": ["400", "normal"],
                "color": [
                    "black", "#000000", "rgb(0,0,0)", 
                    normalize_css_value(elem.css("color"))
                ],
            };
            var current_style = {};
            var opened_style = false;
            function close_style() {
                if (!opened_style) {
                    return;
                }
                current_paragraph += "</span>";
                opened_style = false;
            }
            function open_style() {
                if (opened_style) {
                    return;
                }
                var style = "";
                $.each(current_style, function(key, value) {
                    style += key + ": " + value + "; ";
                });
                if (!style) {
                    return;
                }
                current_paragraph += '<span style="' + style + '">';
                opened_style = true;
            }
            function change_style(new_style) {
                if (is_same_style(current_style, new_style)) {
                    return;
                }
                close_style();
                current_style = new_style;
            }
            function get_style(elem) {
                var result = {};
                $.each(default_style, function(key, default_values) {
                    var current_value = normalize_css_value(elem.css(key));
                    if (default_values.indexOf(current_value) === -1)
                    {
                        result[key] = current_value;
                    }
                });
                return result;
            }
            function is_same_style(style1, style2) {
                if (Object.keys(style1).length !== Object.keys(style2).length) {
                    return false;
                }
                var is_same = true;
                $.each(style1, function(key, value) {
                    if (value !== style2[key]) {
                        is_same = false;
                        return true;
                    }
                });
                return is_same;
            }
            function complete_paragraph() {
                if (current_paragraph === "" && 
                    (paragraphs.length === 0 ||
                     paragraphs[paragraphs.length - 1] === "")) {

                    return;
                }
                close_style();
                paragraphs.push(current_paragraph);
                current_paragraph = "";
            }
            function handle_element() {
                var o = $(this);
                if (this.nodeName === "#text") {
                    var content = $.trim(this.textContent).replace(/\n/g, "");
                    if (content) {
                        open_style();
                        current_paragraph += content;
                    }
                    return;
                } else if (this.nodeName === "IMG") {
                    var width = o.width();
                    var height = o.height();
                    if ((width > 0 && width < 64) || 
                        (height > 0  && height < 64)) {
                        // Probably not an image in novel
                        return;
                    }
                    // Discuz X2 places full-sized image in zoomfile
                    var src = o.attr("zoomfile") || 
                              o.attr("src") || 
                              o.attr("file");
                    if (/.*\.gif$/gi.test(src)) {
                        // Nobody will use gif, this must be a face (?)
                        return;
                    }
                    // Convert to absolute URL
                    // May have problem under IE6, but we don't support IE 
                    // so never mind
                    src = $("<a/>").attr("href", src).get(0).href;
                    current_paragraph += '<img src="' + src + '"/>';
                } else if (this.nodeName === "BR") {
                    complete_paragraph();
                } else if (this.nodeName === "TABLE") {
                    // Remove all formatting of the table, 
                    // and sanitize its content
                    o.find("tr, td").andSelf().each(function() {
                        var attrs = $.map(this.attributes, function(item) {
                            return item.name;
                        });

                        var elem = $(this);
                        $.each(attrs, function(i, name) {
                            elem.removeAttr(name);
                        });
                    });
                    o.find("td").each(function() {
                        var cell = $(this);
                        var content_array = build_content(cell);
                        if (content_array.length == 1) {
                            $(this).html(content_array[0]);
                        } else {
                            var content = $.map(content_array, function(item) {
                                return "<p>" + item + "</p>";
                            });
                            $(this).html(content.join(""));
                        }
                    });
                    complete_paragraph();
                    current_paragraph += this.outerHTML;
                } else {
                    var old_style = current_style;
                    if (o.css("display") === "block") {
                        complete_paragraph();
                    }
                    change_style(get_style(o));
                    o.contents().each(handle_element);
                    change_style(old_style);
                }
            }
            $(elem).each(handle_element);
            complete_paragraph();
            while (paragraphs.length > 0 && paragraphs[0] === "") {
                paragraphs.shift();
            }
            while (paragraphs.length > 0 && 
                   paragraphs[paragraphs.length - 1] === "") {
                paragraphs.pop();
            }
            return paragraphs;
        }

        function do_extract() {
            var elems = $(CONTENT_ELEM_SELECTOR).filter(function() {
                return is_content_elem($(this));
            }).clone();
            elems.each(preprocess_elem);
            var contents = $.map(elems, function(elem) {
                // jQuery will flatten the returned array, so we need to wrap
                // it in another one
                return [build_content(elem)];
            });
            var script_node = $("#novel-extractor");
            var prefix = /^(https?:\/\/.+?\/).*/i.exec(
                script_node.attr("src")
            )[1];
            var importer_url = prefix + "novel-importer/import-from-external";
            var form = $("<form/>");
            form.attr({
                "accept-charset": "utf-8",
                action: importer_url,
                method: "post"
            });
            $("<input/>").attr({
                type: "hidden",
                name: "content_json"
            }).val(JSON.stringify(contents)).appendTo(form);
            $("<input/>").attr({
                type: "hidden",
                name: "site_cookies_json"
            }).val(JSON.stringify(document.cookie)).appendTo(form);
            form.appendTo("body").submit();
        }

        do_extract();
        $.noConflict();
    };
    document.head.appendChild(node);

})();
