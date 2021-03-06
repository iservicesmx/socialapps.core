from django import template
from django.db import models

from ..utils import has_permission
register = template.Library()

@register.inclusion_tag('local_menu.html', takes_context = True)
def show_local_menu(context, parent = None, current = 'index'):
    if isinstance(parent, models.Model):
        for ancestor in parent.get_parents(True):
            parent = ancestor.get_type_object()
            if hasattr(parent, 'get_local_menu'):
                menu = parent.get_local_menu(context['user'])['items']
                absolute_url = parent.get_absolute_url()
                if not [item for item in menu if item['id'] == current ]:
                    current = 'index'
                return {'options' : menu, 'absolute_url':absolute_url ,'current' : current }

class PermissionComparisonNode(template.Node):
    """Implements a node to provide an if current user has passed permission 
    for current object.
    """
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) < 3:
            raise template.TemplateSyntaxError(
                "'%s' tag takes at least two arguments" % bits[0])
        end_tag = 'endifhasperm'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag:
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(nodelist_true, nodelist_false, *bits[1:])

    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.args = args

    def render(self, context):
        obj = context.get(self.args[len(self.args) - 1])
        request = context.get("request")
        perm = has_permission(obj, request.user, *self.args[:-1])
        if perm:
            return self.nodelist_true.render(context)
        if type(self.nodelist_false) == str:
            return self.nodelist_false
        else:
            return self.nodelist_false.render(context)

@register.tag
def ifhasperm(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNode.handle_token(parser, token)
