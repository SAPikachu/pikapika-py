define(["require", "jquery", "underscore", "backbone", "jstorage", "ajax-call"],
function(require,   $,        _,            Backbone) {

var LocalBackedModel = Backbone.Model.extend({
    save_local: function() {
        $.jStorage.set(this.url(), this.toJSON());
    },
    fetch_local: function() {
        this.set($.jStorage.get(this.url(), {}));
    }
});

var reader_styles = new LocalBackedModel();
function update_reader_styles(model) {
    var old_classes = document.documentElement.className.split(" ");
    var new_classes = _.chain(old_classes).
        reject(function(cls) { return /^rs-([\w\-]+)--(.+)$/.test(cls); }).
        union(_.map(model.toJSON(), function(value, key) {
            return _.template("rs-<%= key %>--<%= value %>", data={
                key: key,
                value: value
            });
        })).
        value();

    document.documentElement.className = new_classes.join(" ");
    model.save_local();
};

reader_styles.on("change", update_reader_styles);
reader_styles.urlRoot = "/profile/reader_styles";
reader_styles.fetch_local();

$("#reader-style-settings .style-group > span").click(function() {
    reader_styles.set($(this).parent().data("key"), this.className);
});

$(function() {
    // ----- auto-scrolling
    var auto_scroll_enabled = false;
    var auto_scroll_interval = 100;
    function do_auto_scroll() {
        if (!auto_scroll_enabled) {
            return;
        }
        window.scrollBy(0, 5);
        setTimeout(do_auto_scroll, auto_scroll_interval);
    }

    $("#page article").dblclick(function (e) {
        if (window.getSelection) {
            window.getSelection().removeAllRanges();
        }
        else if (document.selection) { // should come last; Opera!
            document.selection.empty();
        }
        auto_scroll_enabled = true;
        do_auto_scroll();
        e.preventDefault();
        return false;
    });

    $(document).mousedown(function () {
        auto_scroll_enabled = false;
    });

    $(document).keydown(function (e) {
        if (auto_scroll_enabled) {
            if (e.which == 38 || e.which == 40) { // UP and DOWN
                auto_scroll_interval += (e.which - 39) * 10;
                auto_scroll_interval = Math.max(Math.min(autoScrollInterval, 300), 10);
                e.preventDefault();
                return false;
            }
        }
    });

    // ----- navigation hotkey
    $(document).keydown(function (e) {
        var link;
        if (e.which == 37) { // LEFT
            link = $("#link-prev-page").attr("href");
        } else if (e.which == 39) { // RIGHT
            link = $("#link-next-page").attr("href");
        }
        if (link) {
            location.href = link;
        }
    });

    // ----- track hits
    // Intentionally put in ready handler for convenience, since it doesn't
    // really matter how long it takes to track the hit
    $.post(
        URLS.hit,
        { hitcount_pk: HITCOUNT_PK },
        function(data) {
            if (data.hits) {
                $("#hit-count").text(data.hits);
            }
        },
        "json"
    );
});

});

