(function ($) {
    var activity_indicator;
    function activity_switch(state) {
        var indicator_size = 48;
        if (!activity_indicator) {
            if (!state) {
                return;
            };
            activity_indicator = {
                indicator: $("<div/>").
                    attr("id", "activity-indicator").
                    css({
                        position: "fixed",
                        width: indicator_size,
                        height: indicator_size
                    }).
                    appendTo("body"),
                overlay: $("<div/>").
                    addClass("ui-widget-overlay").
                    css({
                        position: "absolute",
                        top: 0,
                        left: 0,
                        zIndex: 1000
                    }).
                    appendTo("body")
            };
        };
        activity_indicator.indicator.css({
            left: ($(window).width() - indicator_size) / 2,
            top: ($(window).height() - indicator_size) / 2
        }).activity(state ? {zIndex: 1001} : false);
        activity_indicator.overlay.css({
            width: $(document).width(),
            height: $(document).height()
        }).toggle(state);
    }
    $.fn.submodelInline = function(inline_params) {
        var container = $(this).find("tbody, .grp-table");
        var row_selector = "> .has_original";
        var id_selector = "input[type=hidden][name$=-id]";
        var error_dialog;
        container.find(row_selector).dblclick(function(e) {
            if (e.target.nodeName.toLowerCase() === "div") {
                location.href = inline_params.url_prefix.replace("-1", $(this).find(id_selector).val());
            };
        });
        if (inline_params.sortable) {
            container.sortable({
                items: row_selector,
                axis: "y",
                placeholder: "grp-module ui-sortable-placeholder",
                forceHelperSize: true,
                forcePlaceholderSize: true,
                stop: function() {
                    var rows = container.find(row_selector);
                    rows.removeClass("row1 row2");
                    rows.filter(":even").addClass("row1");
                    rows.filter(":odd").addClass("row2");
                    var order = $.map(rows, function(elem) {
                        return $(elem).find(id_selector).val();
                    }).join(",");
                    activity_switch(true);
                    var post_params = {
                        app_label: inline_params.app_label,
                        parent_model_name: inline_params.parent_model_name,
                        parent_model_pk: inline_params.parent_model_pk,
                        relation_name: inline_params.relation_name,
                        order: order
                    };
                    $.ajax({
                        url: "/ajax/admin/set_model_order", 
                        type: "POST",
                        data: post_params,
                        dataType: "json",
                        error: function(xhr, textStatus, errorThrown) {
                            if (!error_dialog) {
                                error_dialog = $("<div/>").
                                    appendTo("body").
                                    dialog({
                                        autoOpen: false,
                                        resizable: false,
                                        title: "Error"
                                    });
                            };
                            error_dialog.text("Unable to reorder the objects, status: " + textStatus + ", error: " + errorThrown);
                            error_dialog.dialog("open")
                        },
                        complete: function() { activity_switch(false); }
                    });
                }
            });
        };
    };
})(jQuery);

