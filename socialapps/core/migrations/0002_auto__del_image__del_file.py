# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Image'
        db.delete_table('core_image')

        # Deleting model 'File'
        db.delete_table('core_file')


    def backwards(self, orm):
        
        # Adding model 'Image'
        db.create_table('core_image', (
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('image', self.gf('socialapps.core.fields.thumbs.ImageWithThumbsField')(max_length=100)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('efective', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(blank=True, max_length=100, db_index=True)),
            ('position', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Image'])

        # Adding model 'File'
        db.create_table('core_file', (
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('efective', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(blank=True, max_length=100, db_index=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['File'])


    models = {
        
    }

    complete_apps = ['core']
