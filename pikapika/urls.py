from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from filebrowser.sites import site

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pikapika.views.home', name='home'),
    url(r'^ajax/', include('pikapika.ajax_services.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^novel-importer/', 
        include('pikapika.novel_importer.urls', 
                app_name="novel_importer",
                namespace="novel_importer",),
       ),
    url(r'^', include('pikapika.novel.urls')),
)

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              urlpatterns
