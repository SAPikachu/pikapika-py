from django.conf.urls import patterns, url

urlpatterns = patterns('pikapika.novel_importer.views',
    url(r'^import-from-external$', 'import_from_external'),
    url(r'.*_MEDIA_URL_(?P<path>.*)$', "redirect_media"),
    url(r'^(?P<page_name>[^/]+)$', 'static_view'),
)

