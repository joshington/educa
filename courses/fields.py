# Django comes with a complete collection of model fields that you
# can use to build your models. However, you can also create your
# own model fields to store custom data or alter the behavior of
# existing fields.
# We need a field that allows us to define an order for objects. An easy
# way to specify an order for objects using existing Django fields is by
# adding a PositiveIntegerField to your models. Using integers, we can
# easily specify the order of objects. We can create a custom order
# field that inherits from PositiveIntegerField and provides additional
# behavior.
# There are two relevant functionalities that we will build into our
# order field:

# Automatically assign an order value when no
# specific order is provided: When saving a new object
# with no specific order, our field should automatically assign
# the number that comes after the last existing ordered object.
# If there are two objects with order 1 and 2 respectively, when
# saving a third object, we should automatically assign the
# order 3 to it if no specific order has been provided.
# Order objects with respect to other fields: Course
# modules will be ordered with respect to the course they
# belong to and module contents with respect to the module
# they belong to.



from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import fields, query



#our custom OrderField inherits from the PositiveIntegerField field provided by Django
#our OrderField field takes an optional for_fields parameter that allows us to indicate the fields
#that the order has to be calculated with respect to

#==ourfield overrides the pre_save() mthd of the PositiveIntegerField field, which is executed
#before saving the field into the database.in this mthd we perform the follwoing actions

#1-we check if a value alerady exists for this field in the model instance,we use self.attname,which
# is the attribute name given to the field in the model.if the attribute's value is different than
# None,we calculate the order we should give it as follows
# 1==.  we build a queryset to retiriev all objects for the field's model.we retrieve the model 
# class the field belongs to by accessing self.model 
#we filter the queryset by the fields' current value for the model fields 
class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields=for_fields
        super(OrderField, self).__init__(*args, **kwargs)


    def pre_save(self, model_instance, add: bool):
        if getattr(model_instance, self.attname) is None:
            #no current value
            try:
                qs = self.model.objects.all()#retrieve all objects for the field's model
                #retrieve the model class the field belongs to by accessing self.model
                if self.for_fields:
                    #filter by objects with the same field values
                    #for the fields in for_fields
                    query={field: getattr(model_instance, field) for field in self.for_fields}
                    qs=qs.filter(**query)
                    #filter the queryset by the fields' current value for the model fields that 
                    #are defined in the for_fields parameter of the field,if anyby doing so we 
                    #calculate the order with respect to the given fields
                #get the order of the last item
                last_item = qs.latest(self.attname)#retrieve the object with the highest order with
                #from the database.
                value = last_item.order+1#if an object is found, we add 1 to the highest order found
            except ObjectDoesNotExist:
                value = 0
            #if no object is found,we assume this object is the fiest one and assign the order 0 to it
            setattr(model_instance, self.attname, value)#we asign the calculated order to the field's
            #value in the model instance using setattr() AND RETURN IT
            return value
        else:
            return super(OrderField,self).pre_save(model_instance, add)
#if the model instance has avalue for the current field,we dont do anything
#wen you create custom model fields, make them generic.avoid hardcoding data that depends
#on aspecific model or field.your field should work in any model