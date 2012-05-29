from django.conf.urls import patterns, url

urlpatterns = patterns('pikapika.novel_importer.views',
    url(r'^import-from-external', 'import_from_external'),
    url(r'^editor', 'editor'),
)

