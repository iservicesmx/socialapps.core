from django.db.models import signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.contrib.sites import models as site_app

from permissions.utils import register_permission, register_role


def create_roles(app, created_models, verbosity, **kwargs):
    roles = {}
    for role in settings.ROLES:
        roles[role] = register_role(role[1])
    register_permission('View', 'view')
    register_permission('Edit', 'edit')
    register_permission('Add', 'add')
    register_permission('Delete', 'delete')
    register_permission('Socialize', 'socialize')
    print "roles creados"
        
signals.post_syncdb.connect(create_roles, sender=site_app)

