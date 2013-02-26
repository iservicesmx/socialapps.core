from django.conf import settings
from django.template import Context
from django.utils.translation import ugettext
from django.template.loader import render_to_string

from notification.backends import email

class EmailCustomBackend(email.EmailBackend):
    site = None
    
    def can_send(self, user, notice_type):
        can_send = super(EmailCustomBackend, self).can_send(user, notice_type)
        if can_send and user.email:
            self.site = user.person.site
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
        
    def deliver(self, recipient, sender, notice_type, extra_context):
        # TODO: require this to be passed in extra_context

        context = self.default_context()
        context.update({
            "recipient": recipient,
            "sender": sender,
            "notice": ugettext(notice_type.display),
        })  
        context.update(extra_context)

        messages = self.get_formatted_messages((
            "short.txt",
            "full.txt"
        ), notice_type.label, context)

        subject = "".join(render_to_string("notification/email_subject.txt", {
            "message": messages["short.txt"],
        }, context).splitlines())

        body = render_to_string("notification/email_body.txt", {
            "message": messages["full.txt"],
        }, context)
        # TODO: remove school dependency
        return {
            'subject': subject,
            'body': body,
            'from': "%s <%s>" % (self.site.school.title, self.site.school.email),
            'to': [recipient.email]
        }
        # # print recipient
        # send_mail(subject, body, "%s <%s>" %(self.site.school.title, self.site.school.email), [recipient.email])
