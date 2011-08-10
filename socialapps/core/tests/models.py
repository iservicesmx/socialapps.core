from datetime import datetime

from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from permissions.utils import register_permission, register_role

from socialapps.core.models import *

class MyBaseDescription(BaseDescription):
    class Meta:
        ordering = ("title",)
        #app_label = 'core'

class MyBaseMetadata(BaseMetadata):
    class Meta:
        ordering = ("title",)
        #app_label = 'core'    

class MyBaseContent(BaseContent):
    class Meta:
        ordering = ("title",)
        #app_label = 'core'    

class MyDummyModel(models.Model):
    foo = models.TextField("Foo", blank=True, null=True)

    
class BaseCase(TestCase):
    def setUp(self):
        """
        Create an admin user.
        """
        #roles = {}
        #for role in settings.ROLES:
        #    roles[role] = register_role(role[1])
            
        self.username = "test"
        self.password = "test"
        args = (self.username, "example@example.com", self.password)
        self.user = User.objects.create_superuser(*args)
        
    def test_my_base_description(self):
        desc = MyBaseDescription(title='My Document', description="Lorem Ipsum")
        desc.save()
        self.assertEqual(desc.slug, 'my-document')
        
        desc2 = MyBaseDescription(title='My Document', description="Maquade sum")
        desc2.save()
        self.assertEqual(desc2.slug, 'my-document-1')
        
        desc3 = MyBaseDescription(title='My Document', description="Blah, Blah, Blah")
        desc3.save()
        self.assertEqual(desc3.slug, 'my-document-2')
        
        self.assertNotEqual(desc.slug,desc2.slug)
        self.assertNotEqual(desc.slug,desc3.slug)
        self.assertNotEqual(desc2.slug,desc3.slug)

    def test_my_base_metadata(self):
        meta1 = MyBaseMetadata(creator=self.user,title='My Metadata')
        meta1.save()
        modified_pre_meta1 = meta1.modified
        
        self.assertEqual(meta1.slug, u'my-metadata')
        self.assertTrue(meta1.created < meta1.modified)
        
        meta2 = MyBaseMetadata(creator=self.user,title='My Metadata')
        meta2.save()
        self.assertNotEqual(meta1.slug, meta2.slug)        
        
        foo = MyDummyModel(foo="Lorem Ipsum")
        
        meta1 = MyBaseMetadata.objects.get(id=meta1.id)
        meta1.title = 'Your Metadata'
        meta1.save()
        
        self.assertTrue(meta1.modified > modified_pre_meta1)
        self.assertEqual(meta1.slug, u'my-metadata')
    
    def test_my_base_content(self):
        pass
    
class BaseGroupCase(TestCase):
    def setUp(self):
        """
        Create an admin user.
        """
        self.username = "test2"
        self.password = "test2"
        args = (self.username, "example2@example.com", self.password)
        self.user = User.objects.create_superuser(*args)
    