// Keep/restore jQuery in global namespace, it may be hidden by django or
// grappelli

window.jQuery = window["jQuery"] || django.jQuery;

window.django = { jQuery: window.jQuery };

