from django.conf.urls.defaults import *
from socialapps import core
from socialapps import cms

cms.autodiscover()

urlpatterns = patterns('',
    (r'^profiles/', include('socialapps.profile.urls')),
    (r'^messages/', include('socialapps.dmessages.urls')),
)

urlpatterns += patterns('socialapps.core.views',
    url(r'^$', "dashboard", name="core_dashboard"),
    url(r'^demos/$', "test", name="test"),
    url(r'^file/(?P<id>[-\w]*)', "file", name="socialapps_file"),
)

