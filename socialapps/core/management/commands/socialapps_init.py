# django imports
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

from socialapps.spaces.models import SpaceRoot

from permissions.utils import register_permission, register_role

class Command(BaseCommand):
    args =''
    help = """Initializes socialapps.core 
    This will create the roles and permissions for spaces.
    """

    def handle(self, *args, **options):
        roles = {}
        for role in settings.ROLES:
            roles[role] = register_role(role[1])
        register_permission('View', 'view')
        register_permission('Edit', 'edit')
        register_permission('Add', 'add')
        register_permission('Delete', 'delete')
        register_permission('Socialize', 'socialize')
        
        SpaceRoot.objects.create(title="spaces", status=1, portal_type="spaceroot")