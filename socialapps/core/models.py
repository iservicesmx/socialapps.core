import os
from datetime import datetime

from django.db import models
from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models.query import QuerySet
from django.forms import model_to_dict

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify, truncatewords_html
from django.utils.translation import ugettext_lazy as _
from django.utils import formats, timezone
from django_bleach.models import BleachField

from tagging.fields import TagField

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
    title = models.CharField(_("Title"), max_length=255, blank=False)
    slug = models.SlugField(_("Slug"), max_length=255, blank=True)
    description = BleachField(verbose_name=_("Description"), blank=True)

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

    def to_dict(self):
        return model_to_dict(self)

    def get_date_string(self, attr):
        tz = timezone.get_current_timezone()
        return formats.date_format(getattr(self, attr).astimezone(tz), "DATETIME_FORMAT")

    @property
    def date_string(self):
        """Formats the created date into a pretty string."""
        return self.get_date_string('created')

    @property
    def effective_string(self):
        """Formats the effective date into a pretty string."""
        return self.get_date_string('efective')

    @property
    def expires_string(self):
        """Formats the expires date into a pretty string."""
        return self.get_date_string('expires')

class Commentable(models.Model):
    comments_count = models.IntegerField(_('total amount of comments'), blank=True, default=0)
    allow_comments = models.BooleanField(_('Allow comments'), blank=True, default=True)

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
