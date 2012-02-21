import sys

import django
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from socialapps.core.socialpanels import SocialPanel
from django.http import Http404, HttpResponse

class ActivityPanel(SocialPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Activity'
    template = 'socialpanels/learningpath.html'
    has_content = True

    def nav_title(self):
        return _('Activity')

    def nav_subtitle(self):
        return 'Django %s' % django.get_version()

    def url(self):
        return ''

    def title(self):
        return _('Versions')

    def process_response(self, request, response):
        self.record_stats({
            'next_object': 'Siguiente',
            'prev_object': 'Anterior',
        })