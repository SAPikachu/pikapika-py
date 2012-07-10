from django.conf.urls import patterns, url

urlpatterns = patterns('pikapika.novel_importer.views',
    url(r'^begin-edit-(?P<volume_id>\d+)$', 'begin_edit', name='begin_edit'),
    url(r'^import-from-external$', 'import_from_external'),
    url(r'^save-ajax$', 'save_volume_ajax'),
    url(r'.*_MEDIA_URL_(?P<path>.*)$', 'redirect_media'),
    url(r'^(?P<page_name>[^/]+)$', 'static_view'),
)

