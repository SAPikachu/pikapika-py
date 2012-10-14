define(["require", "jquery"], function(require, $) {
$(function() {

$(".gsc-search-box").submit(function(e) {
    if (!$.trim($(".gsc-input").val())) {
        e.preventDefault();
        return false;
    }
});

$(".icon-search-button").click(function() {
    $(".gsc-search-box").submit();
});

$(".gsc-input").on("change keyup blur", function() {
    var o = $(this);
    o.toggleClass("have-text", !!o.val());
}).change();

});
});
