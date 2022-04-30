from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
# Create your models here.

from .fields import OrderField
class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug=models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Course(models.Model):
    owner=models.ForeignKey(User,related_name='courses_created',on_delete=models.CASCADE)
    subject=models.ForeignKey(Subject,related_name='courses',on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='courses_joined',blank=True)
    #many to many rxnship for users to login

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course,related_name='modules',on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])
    def __str__(self) -> str:
        return '{}. {}'.format(self.order, self.title)


    class Meta:
        ordering = ['order']

#==we name the new field order,and we specify that the ordering is calculated with respect to 
#the course by setting for_fields=['course].this means that the order for anew module willbe 
#assigned adding 1 to the last module of the same Course object. now,you can edit 

    

#==module contents also need to follow a particular order. add an OrderField field to the
#Content model
class Content(models.Model):
    module=models.ForeignKey(Module,related_name='contents',on_delete=models.CASCADE)
    content_type=models.ForeignKey(ContentType,on_delete=models.CASCADE,limit_choices_to={
        'model__in':('text','video','image','file')
    })
    object_id=models.PositiveIntegerField()
    item=GenericForeignKey('content_type','object_id')
    order=OrderField(blank=True,for_fields=['module'])

    class Meta:
        ordering = ['order']


#we add alimit_choices_to argument to limit the ContentType objects that can be used for the 
#generic rxnship.we use the model__in field lookup to filter the query to the ContentType
#objects with amodel attribute that is; 'text','video','image',or 'file'

#amodule contains multiple contents,so we define aForeignKey field to the Module model
#we also set up ageneric relation to associate objects from different types of content.
#we need 3 different fields to setup ageneric rxnship.
#content_type=>a foreignKey field to the ContentType model
#object_id=>this is PositiveINtegerField to store the primary key of the related object
#item=>A genericForeignKey field to the related object by combining the 2 previous fields

#we are going to use adifferent model foreach type of content.our content models will have some
#common fields, but they will differ in the actual data they can store


#==adding an abstract model to handle the various content types

class ItemBase(models.Model):
    owner=models.ForeignKey(User,related_name='%(class)s_related', on_delete=models.CASCADE)
    title=models.CharField(max_length=250)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

class Text(ItemBase):
    content=models.TextField()

class File(ItemBase):
    file=models.FileField(upload_to='files')

class Image(ItemBase):
    file=models.FileField(upload_to='images')

class Video(ItemBase):
    url=models.URLField()

#WE HAVE DEFINED FOUR DIFFERENT content models,which inherit from the ItemBase abstract model
#Text=>To store text content
#file=>to store files,such as PDF
#Image:to store image files
#video=>store videos,we use an URLField to provide a video URL inorder to embed it