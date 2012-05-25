import thread
import os
import sys

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.utils.functional import curry
from django.utils.datastructures import SortedDict
from django.core import exceptions
from django.utils.encoding import smart_unicode
from django.template.loader import render_to_string

from django.contrib.sites.models import Site

HOST_SITE_TIMEOUT = getattr(settings, "HOST_SITE_TIMEOUT", 3600)

class HostSiteMiddleware(object):
    
    def process_request(self, request):
        host = request.get_host()
        cache_key = "host:%s" % host
        site = cache.get(cache_key, None)        
        
        if not site:
            try:
                site = Site.objects.get(domain__iexact=host)
            except Site.DoesNotExist:
                site = Site.objects.get_current()
                
                if not settings.DEBUG:
                    raise Http404
                    
            cache.set(cache_key, site, HOST_SITE_TIMEOUT)
        
        request.site = site


def replace_insensitive(string, target, replacement):
    """
    Similar to string.replace() but is case insensitive
    Code borrowed from: http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else:  # no results so return the original string
        return string

class SocialToolbar(object):
    def __init__(self, request):
        self.request = request
        self._panels = SortedDict()
        self.load_panels()
        self.stats = {}

    def _get_panels(self):
        return self._panels.values()
    panels = property(_get_panels)

    def get_panel(self, cls):
        return self._panels[cls]

    def load_panels(self):
        from socialapps.core.socialpanels.activity import ActivityPanel
        try:
            panel_class = ActivityPanel
        except AttributeError:
            raise exceptions.ImproperlyConfigured, 'Toolbar Panel module "%s" does not define a "%s" class' % (panel_module, panel_classname)
        try:
            panel_instance = panel_class()
        except:
            raise  # Bubble up problem loading panel
        
        self._panels[panel_class] = panel_instance

    def render_toolbar(self):
        """
        Renders the overall Toolbar with panels inside.
        """
        media_path = os.path.join(os.path.dirname(__file__), os.pardir, 'media', 'debug_toolbar')

        context = {}
        context.update({
            'panels': self.panels,
            # 'js': mark_safe(open(os.path.join(media_path, 'js', 'toolbar.min.js'), 'r').read()),
            # 'css': mark_safe(open(os.path.join(media_path, 'css', 'toolbar.min.css'), 'r').read()),
        })        
        return render_to_string('socialpanels/base.html', context)

class SocialToolbarMiddleware(object):
    """
    Middleware to set up Debug Toolbar on incoming request and render toolbar
    on outgoing response.
    """
    debug_toolbars = {}

    @classmethod
    def get_current(cls):
        return cls.debug_toolbars.get(thread.get_ident())

    def __init__(self):
        self.tag = u'</body>'
        
    def process_request(self, request):
        toolbar = SocialToolbar(request)
        for panel in toolbar.panels:
            panel.process_request(request)
        self.__class__.debug_toolbars[thread.get_ident()] = toolbar

    def process_response(self, request, response):
        __traceback_hide__ = True
        ident = thread.get_ident()
        toolbar = self.__class__.debug_toolbars.get(ident)
        if not toolbar:
            return response
        for panel in toolbar.panels:
            panel.process_response(request, response)
        response.content = replace_insensitive(
            smart_unicode(response.content),
            self.tag,
            smart_unicode(toolbar.render_toolbar() + self.tag))
        return response