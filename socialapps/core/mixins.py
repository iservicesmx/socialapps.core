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
        obj = None
        if hasattr(self, 'perm_object'):
            obj = self.perm_object()
        elif hasattr(self, 'get_object'):
            obj = self.get_object()
        if obj:
            perm = has_permission(obj, request.user, self.permission)
            if perm:
                return super(PermissionMixin, self).dispatch(request, *args, **kwargs);
            raise Http404
        raise Http404
