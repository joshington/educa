from rest_framework.permissions import BasePermission 

class IsEnrolled(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()
        #we check tht the userperforming the request is present in the students rxnship of the
        #Course object