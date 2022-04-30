#from attr import fields
from rest_framework import serializers
from ..models import Subject,Course,Module,Content


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']




class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']



class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()

class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content 
        fields = ['order', 'item']

#we define acustom field by subclassing the RelatedField serializer field provided by
#RF and overriding the to_representation() mthd 
# We define the ContentSerializer serializer for
#the Content model and use the custom field for the item generic foreign
#key.

#==an alternate serializer for the Module model that includes its contents and an extended
#Course serializer as well.

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    #indicate many=True to indicate that we are serializing multipple objects
    #read_only param indicates that this field is read_only and should not be included in any 
    #input to create or update objects.
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview','created', 'owner', 'modules']


#we need to serialize course contents

class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order','title','description','contents']

class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    class Meta:
        model = Course 
        fields = ['id','subject','title','slug','overview','created','owner','modules']

