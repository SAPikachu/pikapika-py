(function($) {
    var dmp = new diff_match_patch();
    dmp.Diff_Timeout = 0.0;

    var SPLITTER_MARK = "$$$SPLITTER$$$";

    var array_view = function(array, start_index, converter) {
        if (!converter) {
            converter = function(value) { return value; };
        }
        return {
            array: array,
            start_index: start_index,
            get: function(index) {
                return converter(this.array[index + this.start_index]);
            },
            size: function() {
                return this.array.length - this.start_index;
            }
        }
    };

    var line_obj_converter = function(line_obj) {
        if (line_obj.type === "splitter") {
            return SPLITTER_MARK;
        }
        return line_obj.data;
    };

    var trim_line = function(line_text) {
        // Note: This is single-line version, the one in prepare_paragraphs is
        // for multi-line text
        return line_text.replace(
            /^(?:&nbsp;|\s)*(.*?)(?:&nbsp;|\s)*$/g, "$1"
        );
    };

    var prepare_paragraphs = function(content) {
        if ($.isArray(content)) {
            // Content is from extractor script, just flatten it
            return $.map(content, function(chapter) { 
                return $.merge($.merge([], chapter), [SPLITTER_MARK]); 
            });
        }
        // Trim all lines
        content = content.replace(
            /^(?:&nbsp;|\s)*(.*?)(?:&nbsp;|\s)*$/gm, "$1"
        );
        // Collapse multiple empty lines to 2 maximum
        content = content.replace(/\n\n+/g, "\n\n");
        return content.split(/\n/g);
    };

    var is_same_line = function(line1, line2) {
        var whitespace_re = /(\s|&nbsp;)/g;
        return line1.replace(whitespace_re, "") === 
            line2.replace(whitespace_re, "");
    };

    var is_image_line = function(line_text) {
        return /^<img [^>]+>$/i.test(line_text);
    };

    var is_empty_line = function(line_text) {
        return trim_line(line_text) === "";
    };

    // https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/String/fromCharCode
    var fixedFromCharCode = function(codePt) {  
        if (codePt > 0xFFFF) {  
            codePt -= 0x10000;  
            return String.fromCharCode(0xD800 + (codePt >> 10), 0xDC00 +  
    (codePt & 0x3FF));  
        }  
        else {  
            return String.fromCharCode(codePt);  
        }  
    };

    var merge_line = function(old_line, new_line) {
        var tag_mappings = {};
        // 0xF0000 - 0xFFFFF = Private Use Area, reserve first 0x400 code
        // points for special tags
        var code_point = 0x0F0400;
        var code_separator = fixedFromCharCode(0x0F0000);

        var replace_tag = function(tag) {
            var code = null;
            $.each(tag_mappings, function(key, value) {
                if (value === tag) {
                    code = key;
                    return false;
                }
            });
            if (!code) {
                code = fixedFromCharCode(code_point);
                code_point++;
                tag_mappings[code] = tag;
            }
            return code_separator + code;
        }
        var tag_re = /<[^>]+>/g;
        // Note: Since code point starts from U+F0400, lead surrogate starts
        // from 0xDB81
        var code_re = /[\uDB81-\uDBFF][\uDC00-\uDFFF]/g;

        var stripped_old_line = old_line.replace(tag_re, replace_tag);
        // Ensure lead surrogates are different
        code_point += 0x400;
        var stripped_new_line = new_line.replace(tag_re, replace_tag);

        var diff = dmp.diff_main(stripped_old_line, stripped_new_line);
        var result = "";
        for (var i = 0; i < diff.length; i++) {
            var code = diff[i][0];
            var text = diff[i][1].replace(new RegExp(code_separator, "g"), "");
            if (code === DIFF_EQUAL || code === DIFF_INSERT) {
                result += text;
            } else {
                // Keep HTML tags from original text
                var match;
                while ((match = code_re.exec(text)) !== null) {
                    result += match[0];
                }
            }
        }
        result = result.replace(code_re, function(code) {
            return tag_mappings[code];
        });
        // Clean up possibly unclosed tags
        result = $("<div/>").html(result).html();
        return result;
    };

    // haystack and needle should be array_view
    // Returns starting index of match in haystack, or -1 if no match
    // Note: The index is relative to start_index of the view.
    var match_multiple = function(params) {

        haystack = params.haystack;
        needle = params.needle;
        max_distance = params.max_distance;
        match_count = params.match_count;

        var current_match_count = 0;
        for (var i = 0; i < max_distance; i++) {
            if (i >= haystack.size()) {
                return -1;
            }
            if (haystack.get(i) === SPLITTER_MARK) {
                return -1;
            }
            if (is_same_line(haystack.get(i), 
                             needle.get(current_match_count)
            )) {
                current_match_count++;
                if (current_match_count >= match_count || 
                    current_match_count === needle.size() ||
                    needle.get(current_match_count) === SPLITTER_MARK) {

                    return i - current_match_count + 1;
                }
            } else {
                // Rollback to the original element, so after i++ we will be on
                // the next element
                i -= current_match_count;
                current_match_count = 0;
            }
        }
        return -1;
    };

    // Returns:
    // null => No changes to this line needed
    // An array of line objects => Lines ready to be spliced into original
    //                             content
    var compute_diff_line = function(line_index, new_paragraphs) {
        var line_obj = novel_importer.clone_line(
            novel_importer.lines[line_index], false
        );
        if (line_obj.type !== "paragraph") {
            return null;
        }
        // Strip leading chapter splitters
        for (var i = 0; i < new_paragraphs.length; i++) {
            if (new_paragraphs[i] === SPLITTER_MARK) {
                new_paragraphs.splice(0, i + 1);
                i = 0;
                continue;
            } else if (new_paragraphs[i]) {
                break;
            }
        }
        if (is_same_line(line_obj.data, new_paragraphs[0])) {
            // No change needed
            new_paragraphs.shift();
            return null;
        }
        // Notes:
        // 1. "current line" => novel_importer.lines[line_index]
        // 2. Do not cross chapter boundary on searching
        // Steps:

        // If first line in new_paragraphs is an image, search nearby 
        // (+/- 20 lines) to see if there is a match, if not, insert it 
        // before current line and continue, otherwise remove it and
        // restart matching.
        if (is_image_line(new_paragraphs[0])) {
            var already_in_existing_lines = false;

            var check_line = function(line_index) {
                var searching_line = novel_importer.lines[i];
                if (searching_line.type === "splitter") {
                    
                    return true;
                }
                if (searching_line.data === new_paragraphs[0]) {
                    already_in_existing_lines = true;
                    return true;
                }
            };
            for (var i = line_index - 1; 
                 i >= Math.max(0, line_index - 20); 
                 i--) {

                if (check_line(i)) {
                    
                    break;
                }
            }
            if (!already_in_existing_lines) {
                for (var i = line_index + 1; 
                     i <= Math.min(novel_importer.lines.length - 1, 
                                   line_index + 20); 
                     i++) {

                    if (check_line(i)) {
                        
                        break;
                    }
                }
            }
            // Match current line with next line in new_paragraphs, repeat the
            // whole process if necessary, and merge the result.

            // Build line object here, to make chapter ID look better, since
            // this line will be placed before lines from future calls (if it
            // is a new line)
            var img_line = novel_importer.make_paragraph(
                new_paragraphs.shift()
            );
            var real_result = compute_diff_line.apply(this, arguments);
            if (!already_in_existing_lines) {
                if (real_result === null) {
                    real_result = [line_obj];
                }
                real_result.unshift(img_line);
            }
            return real_result;
        }

        // Try to find match for first few existing lines, if 
        // found, align current line to that line, and insert skipped lines 
        // as addition.
        var importer_view = array_view(
            novel_importer.lines, line_index, line_obj_converter
        );
        var new_paragraph_view = array_view(new_paragraphs, 0);
        var MAX_DISTANCE = 100;
        var DEFAULT_MATCH_COUNT = 5;

        var match_count = 
            is_image_line(line_obj.data) ? 1 : DEFAULT_MATCH_COUNT;

        var match_in_new_paragraphs = match_multiple({
            haystack: new_paragraph_view,
            needle: importer_view,
            max_distance: MAX_DISTANCE,
            match_count: match_count
        });
        if (match_in_new_paragraphs !== -1) {
            var result = $.map(
                new_paragraphs.splice(0, match_in_new_paragraphs + 1), 
                function(line_text) {
                    return novel_importer.make_paragraph(line_text);
                }
            );
            // Replace the matching line with the original line object, but use
            // new text
            var matched_line = result.pop();
            line_obj.data = matched_line.data;
            result.push(line_obj);

            return result;
        }

        // Skip current line if it is an image
        if (is_image_line(line_obj.data)) {
            return null;
        }

        // Match first few lines from new paragraphs, if found, delete lines
        // before the match
        var match_in_existing_paragraphs = match_multiple({
            haystack: importer_view,
            needle: new_paragraph_view,
            max_distance: MAX_DISTANCE,
            match_count: match_count
        });
        if (match_in_existing_paragraphs !== -1) {
            // Mark current line as deleted, following lines will be marked in
            // future calls, don't optimize until we get performance problems
            return [];
        }

        // Mismatched empty line should not affect real matching
        if (is_empty_line(line_obj.data)) {
            return [];
        }

        // If we can't find matching line, merge current line with the
        // first line in new_paragraphs
        return [$.extend(
            {}, 
            line_obj, 
            { data: merge_line(line_obj.data, new_paragraphs.shift()) }
        )];
    };

    var compute_diff = function(new_paragraphs) {
        var diff_result = {};
        var unsync_score = 0;
        var pending_paragraphs = $.merge([], new_paragraphs);
        var paragraphs_from_sync_point = $.merge([], pending_paragraphs);
        new_paragraphs = null; // To prevent coding error
        var pending_diff = {};
        var skip_to_next_chapter = false;

        var lines_in_this_chapter = 0;
        var unsynced_lines_in_this_chapter = 0;

        var SYNC_THRESHOLD = 10;
        var UNSYNC_TOLERENCE = 100;
        var MAX_UNSYNC_RATE_PER_CHAPTER = 0.6;

        var merge_pending_diff = function() {
            $.extend(diff_result, pending_diff);
            pending_diff = {};
            paragraphs_from_sync_point = 
                $.merge([], pending_paragraphs);
        };
        var drop_pending_diff = function() {
            pending_diff = {};
            unsync_score = Math.min(unsync_score, UNSYNC_TOLERENCE / 2);
            pending_paragraphs = 
                $.merge([], paragraphs_from_sync_point);
        };

        // Result item : {  
        //      index: <index in current lines>, 
        //      new_lines: [<0 or more line object>] 
        // }
        // So that new_lines can be spliced into novel_importer.lines
        for (var i = 0; i < novel_importer.lines.length; i++) {
            var current_line = novel_importer.lines[i];
            if (current_line.type === "splitter") {
                if (skip_to_next_chapter) {
                    skip_to_next_chapter = false;
                } else if (lines_in_this_chapter > 0 &&
                    unsynced_lines_in_this_chapter / lines_in_this_chapter >
                        MAX_UNSYNC_RATE_PER_CHAPTER) {

                    drop_pending_diff();
                } else if (unsync_score < SYNC_THRESHOLD) {
                    merge_pending_diff();
                }
                lines_in_this_chapter = 0;
                unsynced_lines_in_this_chapter = 0;
                continue;
            }
            if (skip_to_next_chapter) {
                continue;
            }
            lines_in_this_chapter++;
            var diff = compute_diff_line(i, pending_paragraphs);
            if (diff !== null) {
                pending_diff[i] = diff;
                unsync_score += Math.max(1, diff.length);
                unsynced_lines_in_this_chapter++;
                if (unsync_score > UNSYNC_TOLERENCE) {
                    drop_pending_diff();
                    skip_to_next_chapter = true;
                }
            } else {
                unsync_score = Math.floor(unsync_score / 2);
            }
        }
        if (unsync_score < SYNC_THRESHOLD) {
            merge_pending_diff();
        } else {
            drop_pending_diff();
        }
        // Remove empty lines at the end
        while (pending_paragraphs.length > 0) {
            var last_item = pending_paragraphs[pending_paragraphs.length - 1];
            if (is_empty_line(last_item) || last_item === SPLITTER_MARK) {
                pending_paragraphs.pop();
            } else {
                break;
            }
        }
        if (pending_paragraphs.length > 0) {
            // Append remaining lines to the end
            diff_result[novel_importer.lines.length] = 
                $.map(pending_paragraphs, function(line_text) {
                    if (line_text === SPLITTER_MARK) {
                        return novel_importer.make_splitter();
                    } else {
                        return novel_importer.make_paragraph(line_text);
                    }
                });
        }
        return diff_result;
    };

    novel_importer.build_diff = function(new_content) {
        var sanitized_new_content = prepare_paragraphs(new_content);

        var diff = compute_diff(sanitized_new_content);
        return diff;
    };
})(jQuery);
