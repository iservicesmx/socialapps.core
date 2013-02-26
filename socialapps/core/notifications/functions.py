from django.core.mail import send_mail
from notification.models import *
import gevent

from .backends import EmailCustomBackend 

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
    
    current_language = get_language()
    recipients = []

    for user in users:
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = None
        
        if language is not None:
            # activate the user's language
            activate(language)
        for backend in NOTIFICATION_BACKENDS.values():
            if backend.can_send(user, notice_type):
                recipient = backend.deliver(user, sender, notice_type, extra_context)
                if recipient:
                    recipients.append(recipient)
                # sent = False
    if len(recipients) > 0:
        # for item in recipients:
        jobs = [gevent.spawn(send_mail(item['subject'], item['body'], item['from'], item['to'])) for item in recipients]
        sent=True
    # gevent.joinall(jobs)
    # print jobs
    # reset environment to original language
    activate(current_language)
    return sent