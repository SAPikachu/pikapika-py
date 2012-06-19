(function($) {
    window.AutoScroll = function(params) {
        $.extend(
            this,
            {
                scroll_margin: 100,
                speed_factor: 2,
                interval: 100,
                dx: 0,
                dy: 0,
                interval_token: null
            },
            params || {}
        );
    };
    $.extend(window.AutoScroll.prototype, {
        do_scroll: function() {
            window.scrollBy(this.dx, this.dy);
        },
        start: function() {
            if (this.interval_token) {
                return;
            }
            var self = this;
            this.interval_token = setInterval(function() {
                self.do_scroll();
            }, this.interval);
        },
        stop: function() {
            clearInterval(this.interval_token);
            this.interval_token = null;
        },
        is_started: function() {
            return !!this.interval_token;
        },
        _get_delta: function(page_pos, page_scroll_pos, viewport_length) {
            var viewport_pos = page_pos - page_scroll_pos;
            viewport_pos = Math.max(0, Math.min(viewport_length, viewport_pos));
            var dist, sign;
            if (viewport_pos < viewport_length / 2) {
                dist = viewport_pos;
                sign = -1;
            } else {
                dist = viewport_length - viewport_pos;
                sign = 1;
            }
            return (Math.max(0, this.scroll_margin - dist) * 
                sign * 
                this.speed_factor);
        },
        set_delta_from_mouse_event: function(e) {
            var win = $(window);
            this.dx = this._get_delta(e.pageX, win.scrollLeft(), win.width());
            this.dy = this._get_delta(e.pageY, win.scrollTop(), win.height());
        }
    });
})(jQuery);
