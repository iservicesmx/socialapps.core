import os
from datetime import datetime

from django.db import models
from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models.query import QuerySet

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify, truncatewords_html
from django.utils.translation import ugettext, ugettext_lazy as _

from tagging.fields import TagField

from socialapps.core.fields import ImageWithThumbsField
from socialapps.core.utils import base_concrete_model

def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_404 and get_list_or_404 more DRY.
    
    Pulled from django.shortcuts
    """
    
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, models.Manager):
        manager = klass
    else:
        manager = klass._default_manager
    return manager.all()

class BaseDescription(models.Model):
    title = models.CharField(_("Title"), max_length=100, blank=True)
    slug = models.SlugField(_("Slug"), max_length=100, blank=True)
    description = models.TextField(_(u"Description"), blank=True)
    
    class Meta:
        abstract = True
        ordering = ("title",)

    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Create a unique slug from the title by appending an index.
        TODO: how much time spend this?
        """
        concrete_model = base_concrete_model(BaseDescription, self)
        if not self.slug:
            self.slug = self.get_slug()
            i = 1
            while concrete_model.objects.filter(slug=self.slug).count() > 0:
                self.slug = self.get_slug() + "-%s" % i
                i += 1
        super(BaseDescription, self).save(*args, **kwargs)
        
    def get_slug(self):
        return slugify(self.title)
        
    def get_type(self):
        pass
    
    
class BaseMetadata(BaseDescription):
    creator  = models.ForeignKey("auth.User",
                    verbose_name=_(u"Creator"), null=True)
    created  = models.DateTimeField(_("Create on"),
                    auto_now_add=True)
    modified = models.DateTimeField(_("Modified on"),
                    auto_now=True, auto_now_add=True) 
    efective = models.DateTimeField(_("Published from"), 
                    blank=True, null=True)
    expires  = models.DateTimeField(_("Expires on"), 
                    blank=True, null=True)
    
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), blank=True, null=True)
    content_id = models.PositiveIntegerField(blank=True, null=True)
    content = generic.GenericForeignKey('content_type', 'content_id')

    tags = TagField()
   
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title
        
    def get_contenttype(self):
        return ContentType.objects.get_for_model(self).id
        
    @property
    def date_string(self):
        """Formats the created date into a pretty string."""                           
        return self.created.strftime("%d of %B of %Y at %H:%M")
                
class BaseContent(BaseMetadata):
    
    body   = models.TextField(_(u"Body"), blank=True)
    
    images = generic.GenericRelation("Image", verbose_name=_(u"Images"),
        object_id_field="content_id", content_type_field="content_type")
    files  = generic.GenericRelation("File", verbose_name=_(u"Files"),
        object_id_field="content_id", content_type_field="content_type")
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title
        
class BaseGroup(BaseMetadata):
    PRIVACY_CHOICES = (
        ('P', _('Public')),
        ('R', _('Authorized')),
    )
    privacy = models.CharField(max_length = 1, choices = PRIVACY_CHOICES, default = 'P')
    image = ImageWithThumbsField(upload_to='images', sizes=((60, 60),), blank=True, null = True)
    
    class Meta(object):
        abstract = True

    def member_queryset(self):
        if not hasattr(self, "_members_field"):
            # look for the common case of a m2m named members (in some cases
            # the related_name of the user FK on the intermediary model might
            # be named members and we need User instances)
            try:
                field = self._meta.get_field("members")
            except FieldDoesNotExist:
                raise NotImplementedError("You must define a member_queryset for %s" % str(self.__class__))
            else:
                self._members_field = field
        else:
            field = self._members_field
        if isinstance(field, models.ManyToManyField) and issubclass(field.rel.to, User):
            return self.members.all()
        else:
            raise NotImplementedError("You must define a member_queryset for %s" % str(self.__class__))

    def user_is_member(self, user):
        return user in self.member_queryset()

    def _content_gfk_field(self, model, join=None, field_name=None):
        opts = model._meta
        if field_name is None:
            field_name = "content"
        if join is not None:
            # see if we can get the model where the field actually lives
            parts = join.split(LOOKUP_SEP)
            for name in parts:
                f, model, direct, m2m = opts.get_field_by_name(name)
                # not handling the model is not None case (proxied models I think)
                if direct:
                    if m2m or f.rel:
                        opts = f.rel.to._meta
                    else:
                        break
                else:
                    opts = f.opts
        try:
            field = [f for f in opts.virtual_fields if f.name == field_name][0]
        except IndexError:
            from django.db.models.loading import cache as app_cache
            model = app_cache.get_model(opts.app_label, opts.module_name)
            raise LookupError("Unable to find generic foreign key named '%s' "
                "on %r\nThe model may have a different name or it does not "
                "exist." % (
                    field_name,
                    model,
                ))
        return field

    def lookup_params(self, model):
        content_type = ContentType.objects.get_for_model(self)
        content_gfk = self._content_gfk_field(model)
        params = {
            content_gfk.fk_field: self.id,
            content_gfk.ct_field: content_type,
        }
        return params

    def content_objects(self, queryable, join=None, gfk_field=None):
        queryset = _get_queryset(queryable)
        content_type = ContentType.objects.get_for_model(self)
        content_gfk = self._content_gfk_field(queryset.model, join=join, field_name=gfk_field)
        if join:
            lookup_kwargs = {
                "%s__%s" % (join, content_gfk.fk_field): self.id,
                "%s__%s" % (join, content_gfk.ct_field): content_type,
            }
        else:
            lookup_kwargs = {
                content_gfk.fk_field: self.id,
                content_gfk.ct_field: content_type,
            }
        content_objects = queryset.filter(**lookup_kwargs)
        return content_objects

    def associate(self, instance, commit=True, gfk_field=None):
        content_gfk = self._content_gfk_field(instance, field_name=gfk_field)
        setattr(instance, content_gfk.fk_field, self.id)
        setattr(instance, content_gfk.ct_field, ContentType.objects.get_for_model(self))
        if commit:
            instance.save()
        return instance

    def get_url_kwargs(self):
        kwargs = {}
        #if hasattr(self, "group") and self.group:
        #    kwargs.update(self.group.get_url_kwargs())

        kwargs.update({"%s_pk" % self._meta.object_name.lower(): self.id})
        return kwargs

        
class Commentable(models.Model):
    comments_count = models.IntegerField(_('total amount of comments'), default=0)
    allow_comments = models.BooleanField(_('Allow comments'),default=True)
    
    class Meta:
        abstract = True

class Voteable(models.Model):
    allow_vote      = models.BooleanField(_('Allow vote'),default=True)
    like_count      = models.IntegerField(_('total amount of like'), default=0)
    dislike_count   = models.IntegerField(_('total amount of dislike'), default=0)
    
    #TODO: change to use a method instead a field
    vote_count      = models.IntegerField(_('total amount of votes'), default=0)

    class Meta:
        abstract = True
