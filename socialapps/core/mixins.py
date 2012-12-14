from django.contrib import messages
from django.http import Http404
from .utils import has_permission
from django.utils.translation import ugettext_lazy as _

class PermissionMixin(object):
    permission = "edit"


    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if hasattr(self, 'get_object'):
            perm = has_permission(self.get_object(), request.user, self.permission)
            if perm:
                return super(PermissionMixin, self).dispatch(request, *args, **kwargs);
            raise Http404
        raise Http404
