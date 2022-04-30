from urllib import request
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..models import Subject,Course
from .serializers import SubjectSerializer,CourseSerializer
from courses.api import serializers 


from .permissions import IsEnrolled 
from .serializers import CourseWithContentsSerializer


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all() 
    serializer_class = SubjectSerializer 

class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

#aview for users to enroll inc ourses
#   
class CourseEnrollView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated, )
    def post(self, request, pk, format=None):
        course=get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({'enrolled':True})


# class CourseViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer

#custom view set


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=False,methods=['post'], 
                authentication_classes=[BasicAuthentication],
                permission_classes=[IsAuthenticated]
            )
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled':True})

    @action(detail=False,methods=['get'],serializer_class=CourseWithContentsSerializer,
                authentication_classes=[BasicAuthentication],
                permission_classes=[IsAuthenticated,IsEnrolled])
    def contents(self, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
#we use the detail_route decorator to specify that this action is performed on asingle object
#we specify that only the GET mthd is allowed for this action
#We use both the IsAuthenticated and our custom IsEnrolled
#permissions. By doing so, we make sure that only users
#enrolled in the course are able to access its contents.
#We use the existing retrieve() action to return the Course object.







#we use the detail_route decorator decorator of the framework to specify that this is an action
#to be performed on asingle object.
#the decorator allows us to add custom attributes for the action.we specify that only
#the post mthd is allowed for the view and set the authentication and 