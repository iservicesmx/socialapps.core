import os
from datetime import datetime

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.template.defaultfilters import slugify, truncatewords_html
from django.utils.translation import ugettext, ugettext_lazy as _

from tagging.fields import TagField

from socialapps.core.fields import ImageWithThumbsField
from socialapps.core.utils import base_concrete_model

class BaseDescription(models.Model):
    title = models.CharField(_("Title"), max_length=100, blank=True)
    slug = models.SlugField(_("Name"), max_length=100, blank=True)
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
    
class Image(BaseMetadata):
    position = models.SmallIntegerField(default=999)
    image = ImageWithThumbsField(_(u"Image"), upload_to="uploads",
        sizes=((64, 64), (128, 128), (400, 400), (600, 600), (800, 800)))
        #TODO: Estandarizar tamanos

    class Meta:
        ordering = ("position", )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("gallery.views.photo", (), {"slug" : self.slug})
    get_absolute_url = models.permalink(get_absolute_url)    

class File(BaseMetadata):    
    position = models.SmallIntegerField(default=999)
    file = models.FileField(upload_to="files")

    class Meta:
        ordering = ("position", )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("socialapps_file", kwargs={"id" : self.id})

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]
        
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
