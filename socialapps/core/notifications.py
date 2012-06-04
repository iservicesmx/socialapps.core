from django.conf import settings
from django.template import Context

from notification.backends import email

class EmailCustomBackend(email.EmailBackend):
    site = None
    
    def can_send(self, user, notice_type):
        can_send = super(EmailCustomBackend, self).can_send(user, notice_type)
        if can_send and user.email:
            profile = user.get_profile()
            self.site = profile.site
            return True
        return False
    
    def default_context(self):
        default_http_protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = self.site
        base_url = "%s://%s" % (default_http_protocol, current_site.domain)
        return Context({
            "default_http_protocol": default_http_protocol,
            "current_site": current_site,
            "base_url": base_url
        })