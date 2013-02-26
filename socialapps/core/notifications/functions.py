from django.core.mail import send_mass_mail
# from django.template.loader import render_to_string
from django.template import loader, Context
from django.utils.translation import ugettext
from django.conf import settings

from notification.models import *

import gevent

from .backends import EmailCustomBackend 

#taken from notifications BaseBackend
def get_formatted_messages(formats, label, context):
        """
        Returns a dictionary with the format identifier as the key. The values are
        are fully rendered templates with the given context.
        """
        format_templates = {}
        for format in formats:
            # conditionally turn off autoescaping for .txt extensions in format
            if format.endswith(".txt"):
                context.autoescape = False
            format_templates[format] = loader.render_to_string((
                "notification/%s/%s" % (label, format),
                "notification/%s" % format), context_instance=context)
        return format_templates

def send_now(users, label, extra_context=None, sender=None):
    """
    Creates a new notice.
    
    This is intended to be how other apps create new notices.
    
    notification.send(user, "friends_invite_sent", {
        "spam": "eggs",
        "foo": "bar",
    )
    """
    sent = False
    if extra_context is None:
        extra_context = {}
    
    notice_type = NoticeType.objects.get(label=label)
    recipients = []

    default_http_protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = extra_context.get('from_user').site
    base_url = "%s://%s" % (default_http_protocol, current_site.domain)
    context = Context({
        "default_http_protocol": default_http_protocol,
        "current_site": current_site,
        "base_url": base_url,
        "sender": sender,
        "notice": ugettext(notice_type.display),
    })
    context.update(extra_context)
    
    messages = get_formatted_messages((
            "short.txt",
            "full.txt"
        ), notice_type.label, context)
    context.update({
        'message': messages['short.txt'],
    })
    subject = loader.render_to_string("notification/email_subject.txt", context)
    context.update({
        'message': messages['full.txt']
    })
    body = loader.render_to_string("notification/email_body.txt", context)

    for user in users:
        recipients.append((subject, body, "%s <%s>" % (current_site.school.title, current_site.school.email), [user.email]))
    if len(recipients) > 0:
        gevent.spawn(send_mass_mail(recipients)
        sent=True
    return sent