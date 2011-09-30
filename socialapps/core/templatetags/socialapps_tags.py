from django import template
from django.db import models
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
import re
import permissions.utils

register = template.Library()

@register.inclusion_tag('local_menu.html')
def show_local_menu(parent = None, current = 'index'):
    if isinstance(parent, models.Model):
        parents = [ancestor.get_type_object() for ancestor in parent.get_ancestors(include_self=True)]
        print parents
        for parent in parents:
            if hasattr(parent, 'get_local_menu'):
                menu = parent.get_local_menu()
                absolute_url = parent.get_absolute_url()
                return {'options' : menu, 'absolute_url':absolute_url ,'current' : current }

class PermissionComparisonNode(template.Node):
    """Implements a node to provide an if current user has passed permission 
    for current object.
    """
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 3:
            raise template.TemplateSyntaxError(
                "'%s' tag takes two arguments" % bits[0])
        end_tag = 'endifhasperm'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag:
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(bits[1], bits[2], nodelist_true, nodelist_false)

    def __init__(self, codename, object, nodelist_true, nodelist_false):
        self.codename = codename
        self.object = object
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        obj = context.get(self.object)
        request = context.get("request")
        if permissions.utils.has_permission(obj, request.user, self.codename):
            return self.nodelist_true.render(context)
        else:
            if type(self.nodelist_false) == str:
                return self.nodelist_false
            else:
                return self.nodelist_false.render(context)

@register.tag
def ifhasperm(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNode.handle_token(parser, token)
