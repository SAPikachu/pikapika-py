from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^s/ajax/hit$', 'hitcount.views.update_hit_count_ajax',
        name='hit'),
    url(r'^s/ajax/', include('pikapika.ajax_services.urls')),
    url(r'^s/thumb/(?P<max_width>\d+)x(?P<max_height>\d+)/+(?P<path>.+)$', 
        'pikapika.common.thumbnail.generate',
        name="thumbnail"),

    # IE treat URL of htc and eot files relative to the web page itself instead of css file, so we have to redirect it to correct place
    url(r'(.*/)?PIE.htc$', 
        RedirectView.as_view(
            url=settings.STATIC_URL_SAME_DOMAIN + "misc/PIE.htc", 
            permanent=True,
        )),
    url(r'(?:.*/)?(?P<file>[^/]+.eot)$', 
        RedirectView.as_view(
            url=settings.STATIC_URL + "font/%(file)s", 
            permanent=True,
        )),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
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
