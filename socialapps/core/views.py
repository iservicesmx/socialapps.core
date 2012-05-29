from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.views.generic import edit
from django.views.generic.detail import *
from django.views.generic.list import *
from django.views.generic.base import *

import urllib2
import urllib
import re
from django.utils import simplejson
from django.core import serializers

from socialapps.core.utils import python_to_json



from datetime import date, timedelta
from datetime import datetime
from dateutil import parser

DATE_FORMAT='%m/%d/%Y'



@login_required
def dashboard(request):
    """ Dashboard page """
    return direct_to_template(request, template='dashboard.html',)


class LocalFormView(object):
    action_title    = _("Edit")
    type_title      = _("Object")
    template_name   = 'base_edit.html'
    template_ajax   = 'base_edit_facebox.html'
    template_form   = None
    url_form_post   = None
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name = self.template_ajax
            
        return super(LocalFormView, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        kwargs.update({
                'action_title': self.action_title,
                'type_title': self.type_title,
                'template_form': self.get_template_form(),
                'url_form_post': self.get_url_form_post()
                })
        return super(LocalFormView, self).get_context_data(**kwargs)
        
    def get_template_form(self):
        if not self.template_form:
            return 'base_edit_form.html'
        return self.template_form
    
    def get_url_form_post(self):
        if not self.template_form and not self.url_form_post:
            raise ImproperlyConfigured(
                "No Form POST. Provide a url_form_post.")
        else:
            return self.url_form_post
        
    def form_invalid(self, form):
        if self.request.GET.get('format','html') == 'json':
            err = python_to_json(form.errors)
            return HttpResponse(err, content_type='application/json')
        return super(LocalFormView, self).form_invalid(form)
        
class CreateView(LocalFormView, edit.CreateView):
    action_title    = _("Create")
    type_title      = _("Object")

class UpdateView(LocalFormView, edit.UpdateView):
    action_title    = _("Update")
    type_title      = _("Object")
    
class DeleteView(LocalFormView, edit.DeleteView):
    action_title    = _("Update")
    type_title      = _("Object")
    template_name   = 'base_delete.html'
    template_form   = 'base_delete_form.html'
    

#http://docs.djangoproject.com/en/1.3/topics/class-based-views#more-than-just-html
class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return HttpResponse(python_to_json(context), content_type='application/json')


class JSONDetailView(JSONResponseMixin, BaseDetailView):
    pass

class JSONTemplateView(JSONResponseMixin, TemplateView):
    
    def render_to_response(self, context):
        if self.request.is_ajax():        #if self.request.GET.get('format','html') == 'json':
            return JSONResponseMixin.render_to_response(self, context)
            
        return TemplateView.render_to_response(self, context)

class HybridDetailView(JSONResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format','html') == 'json':
            return JSONResponseMixin.render_to_response(self, context)

        return SingleObjectTemplateResponseMixin.render_to_response(self, context)

class HybridListView(JSONResponseMixin, MultipleObjectTemplateResponseMixin, BaseListView):
    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format','html') == 'json':
            return JSONResponseMixin.render_to_response(self, context)

        return MultipleObjectTemplateResponseMixin.render_to_response(self, context)

class HybridTemplateView(JSONResponseMixin, TemplateView):
    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format','html') == 'json':
            return JSONResponseMixin.render_to_response(self, context)

        return TemplateView.render_to_response(self, context)


def file(request, language=None, id=None):
    """Delivers files to the browser.
    """
    file = get_object_or_404(File, pk=id)
    response = HttpResponse(file.file, mimetype='application/binary')
    response['Content-Disposition'] = 'attachment; filename=%s' % file.title
    return response


