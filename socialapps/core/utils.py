from StringIO import StringIO

# PIL imports
import PIL.ImageFile
import PIL

from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode

def scale_to_min_size(image, min_width, min_height):
    """Returns an image, that isn't smaller than min_width and min_height.
    That means one side is exactly given value and the other is greater.

    This may only makes sense if the image is cut after it is scaled.
    """

    # resize proportinal
    width, height = image.size

    prop_x = float(min_width) / width
    prop_y = float(min_height) / height

    # TODO: Translate to english
    # Die groessere Proportion (oder Faktor oder Quotient) zwischen Soll-Groesse
    # und Ist-Groesse kommt fuer beide Kanten (da proportional) zur Anwendung.
    # Das bedeutet die uebrige Kante ist auf jeden Fall groesser als gewuenscht
    # (da Multiplikation mit Faktor).

    if prop_x > prop_y:
        height = int(prop_x * height)
        image  = image.resize((min_width, height), PIL.Image.ANTIALIAS)
    else:
        width = int(prop_y * width)
        image = image.resize((width, min_height), PIL.Image.ANTIALIAS)

    return image

def scale_to_max_size(image, max_width, max_height):
    """Returns an image, that isn't bigger than max_width and max_height.

    That means one side is exactly given value and the other is smaller. In
    other words the image fits at any rate in the given box max_width x
    max_height.
    """
    # resize proportinal
    width, height = image.size

    # TODO: Translate to english
    # Erechne Proportionen zwischen Soll-Weite und Ist-Weite und zwischen
    # Soll-Hoehe und Ist-Hoehe

    prop_width = float(max_width) / width
    prop_height = float(max_height) / height

    # TODO: Translate to english
    # Die kleinere Proportion (oder Faktor oder Quotient) der beiden kommt fuer
    # beide Kanten (da Proportional) zur Anwendung. Das bedeutet die uebrige
    # Kante ist auf jeden Fall kleiner als gewuenscht (da Multiplikation mit
    # Faktor).

    if prop_height < prop_width:
        width = int(prop_height * width)
        image = image.resize((width, max_height), PIL.Image.ANTIALIAS)
    else:
        height = int(prop_width * height)
        image  = image.resize((max_width, height), PIL.Image.ANTIALIAS)

    return image

def scale_to_width(image, target_width):
    """Returns an image that has the exactly given width and scales height
    proportional.
    """
    width, height = image.size

    prop_width = float(target_width) / width
    new_height = int(prop_width * height)

    image  = image.resize((target_width, new_height), PIL.Image.ANTIALIAS)

    return image

def scale_to_height(image, target_height):
    """Returns an image that has the exactly given height and scales width
    proportional.
    """
    width, height = image.size

    prop_height = float(target_height) / height
    new_width = int(prop_height * width)

    image  = image.resize((new_height, target_height), PIL.Image.ANTIALIAS)

    return image

#From Mezzanine Project
def base_concrete_model(abstract, instance):
    """
    Used in methods of abstract models to find the super-most concrete
    (non abstract) model in the inheritance chain that inherits from the
    given abstract model. This is so the methods in the abstract model can
    query data consistently across the correct concrete model.

    Consider the following::

        class Abstract(models.Model)

            class Meta:
                abstract = True

            def concrete(self):
                return base_concrete_model(Abstract, self)

        class Super(Abstract):
            pass

        class Sub(Super):
            pass

        sub = Sub.objects.create()
        sub.concrete() # returns Super

    In actual Mezzanine usage, this allows methods in the ``Displayable`` and
    ``Orderable`` abstract models to access the ``Page`` instance when
    instances of custom content types, (eg: models that inherit from ``Page``)
    need to query the ``Page`` model to determine correct values for ``slug``
    and ``_order`` which are only relevant in the context of the ``Page``
    model and not the model of the custom content type.
    """
    for cls in reversed(instance.__class__.__mro__):
        if issubclass(cls, abstract) and not cls._meta.abstract:
            return cls
    return instance.__class__
    
#http://docs.djangoproject.com/en/dev/topics/serialization#s-id2
class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj) 

json_encoder = LazyEncoder(ensure_ascii=False)

def python_to_json(obj):
    return json_encoder.encode(obj)
