
#we want to know which type of object each of the item object is:Text,Video,Image,orFile
#we need the model name to build the URl to edit the object.Besides this,
#we could display each item in the template differently based on the type of content it is
#we can get the model for an object from the model's Meta class, by accessing the object's
# _meta attribute. but django doesnt allow accessing variables or attributes starting
# with an underscore in templates to prevent retrieving private attributes or calling
#private mthds. hence we solve this by writing a custom template filter.

from django import template

register = template.Library()

@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name 
    except AttributeError:
        return None
#this is the model_name template filter.we can apply it in templates as object|model_name
#to get the model name for an object.
