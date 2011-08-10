from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.functional import curry

from socialapps.core.bridge import ContainerDummy, ContainerRequestHelper


class ContainerAwareMiddleware(object):
    
    def process_view(self, request, view, view_args, view_kwargs):
        
        bridge = view_kwargs.pop("bridge", None)
        
        if bridge:
            try:
                container = bridge.get_container(view_kwargs)        
            except ObjectDoesNotExist:
                raise Http404
        else:
            container = ContainerDummy()
        
        # attach a request helper
        container.request = ContainerRequestHelper(request, container) # may be is not necesary
        
        request.container = container
        request.bridge = bridge
        
        return None
