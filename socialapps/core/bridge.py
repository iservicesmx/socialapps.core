import sys
import copy

from django.shortcuts import render_to_response
from django.conf.urls.defaults import patterns, url as urlpattern
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, reverse as dreverse

from django.contrib.contenttypes.models import ContentType


class ContainerDummy(object):
    
    def __nonzero__(self):
        return False

class ContainerRequestHelper(object):
    
    def __init__(self, request, container):
        self.request = request
        self.container = container
    
    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        for k, v in self.__dict__.iteritems():
            if k == "request":
                continue
            setattr(obj, k, copy.deepcopy(v, memo))
        obj.request = self.request
        memo[id(self)] = obj
        return obj
    
    def user_is_member(self):
        # Change for permissions
        if not self.request.user.is_authenticated():
            is_member = False
        else:
            if self.container:
                is_member = self.container.user_is_member(self.request.user)
            else:
                is_member = True
        return is_member

class ContentBridge(object):
    
    def __init__(self, container_model, content_app_name=None, urlconf_aware=True):
        self.parent_bridge = None
        self.container_model = container_model
        self.urlconf_aware = urlconf_aware
        
        if content_app_name is None:
            self.content_app_name = container_model._meta.app_label
        else:
            self.content_app_name = content_app_name
        
        # attach the bridge to the model itself. we need to access it when
        # using containerurl to get the correct prefix for URLs for the given
        # container.
        self.container_model.content_bridge = self
    
    def include_urls(self, module_name, url_prefix, kwargs=None):
        if kwargs is None:
            kwargs = {}
        
        prefix = self.content_app_name
        
        __import__(module_name)
        module = sys.modules[module_name]
        
        if hasattr(module, "bridge"):
            module.bridge.parent_bridge = self
        
        urls = []
        
        for url in module.urlpatterns:
            extra_kwargs = {"bridge": self}
            
            if isinstance(url, RegexURLPattern):
                regex = url_prefix + url.regex.pattern.lstrip("^")
                
                if url._callback:
                    callback = url._callback
                else:
                    callback = url._callback_str
                
                if url.name:
                    name = url.name
                else:
                    # @@@ this seems sketchy
                    name = ""
                name = "%s_%s" % (prefix, name)
                
                extra_kwargs.update(kwargs)
                extra_kwargs.update(url.default_args)
                
                urls.append(urlpattern(regex, callback, extra_kwargs, name))
            else:
                # i don't see this case happening much at all. this case will be
                # executed likely if url is a RegexURLResolver. nesting an include
                # at the content object level may not be supported, but maybe the
                # code below works. i don't have time to test it, but if you are
                # reading this because something is broken then give it a shot.
                # then report back :-)
                raise Exception("ContentBridge.include_urls does not support a nested include.")
                
                # regex = url_prefix + url.regex.pattern.lstrip("^")
                # urlconf_name = url.urlconf_name
                # extra_kwargs.update(kwargs)
                # extra_kwargs.update(url.default_kwargs)
                # final_urls.append(urlpattern(regex, [urlconf_name], extra_kwargs))
        
        return patterns("", *urls)
    
    @property
    def _url_name_prefix(self):
        if self.urlconf_aware:
            parent_prefix = ""
            if self.parent_bridge is not None:
                parent_prefix = self.parent_bridge._url_name_prefix
            return "%s%s_" % (parent_prefix, self.content_app_name)
        else:
            return ""
    
    def reverse(self, view_name, container, kwargs=None):
        if kwargs is None:
            kwargs = {}
        
        final_kwargs = {}

        if hasattr(container, "content") and container.content:
            temp_container = container.content
            while temp_container:
                final_kwargs.update({"%s_pk" % temp_container._meta.object_name.lower(): temp_container.id})
                temp_container = temp_container.content

        final_kwargs.update({"%s_pk" % container._meta.object_name.lower(): container.id})
        
        final_kwargs.update(kwargs)
        
        return dreverse("%s%s" % (self._url_name_prefix, view_name), kwargs=final_kwargs)
        
    def container_base_template(self, template_name="content_base.html"):
        return "%s/%s" % (self.content_app_name, template_name)
    
    def get_container(self, kwargs):
        
        lookup_params = {}
        
        if self.parent_bridge is not None:
            parent_container = self.parent_bridge.get_container(kwargs)
            lookup_params.update(parent_container.lookup_params(self.container_model))
        else:
            parent_container = None
        
        pk = kwargs.pop("%s_pk" % self.container_model._meta.object_name.lower())
        
        lookup_params.update({
            "pk": pk,
        })
        
        container = self.container_model._default_manager.get(**lookup_params)
        
        if parent_container:
            # cache parent_container on GFK to prevent database hits later on
            container.content = parent_container
        
        return container
