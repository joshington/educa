from django import forms
from django.contrib.contenttypes import fields
from django.db import models
from django.forms.models import inlineformset_factory
from .models import Course, Module

#since a course , is divided into avariable number of modules, it makes sense to use to use
#formsets to manage them. 
ModuleFormSet = inlineformset_factory(Course, Module, fields=['title','description'],
                    extra=2,can_delete=True)
#inlineformset_factory() function provided by django,inline formsests are asmall 
#abstraction on top of formsets that simplify working with related objects.this function 
#allows us to build amodel formset dynamically for the Module objects related to a Course
#object

#fields== the fields that will be included in each form of the formset
#extra:allows us to set the number of empty forms to display in the formset
#can_delete=>if u set this to True,Django will include a boolean field for each form that will be
#rendered as acheckbox input,it allows u to mark the objects u want to delete

