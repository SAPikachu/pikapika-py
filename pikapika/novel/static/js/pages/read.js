require(["jquery", "underscore", "backbone", "jstorage"], 
function( $,        _,            Backbone) {

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

});

