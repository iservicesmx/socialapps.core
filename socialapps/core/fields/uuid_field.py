from django.db import models
import uuid

class UUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 4 )
        kwargs['blank'] = True
        kwargs['editable'] = False
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        if add :
            value = str(uuid.uuid4())[:4]
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^socialapps\.core\.fields\.uuid_field\.UUIDField"])