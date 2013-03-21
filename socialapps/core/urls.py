from django.conf.urls.defaults import *
from socialapps import core
from socialapps import cms
from .forms import CustomSearchForm
from .views import CustomSearchView

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

urlpatterns += patterns('haystack.views',
    url(r'^search/$', CustomSearchView(
        form_class=CustomSearchForm
    ), name='haystack_search'),
)