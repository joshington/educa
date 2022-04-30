from django import forms
from courses.models import Course

class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.HiddenInput)

# We are going to use this form for students to enroll in courses. The
# course field is for the course in which the user gets enrolled.
# Therefore, it's a ModelChoiceField . We use a HiddenInput widget because we
# are not going to show this field to the user. We are going to use this
# form in the CourseDetailView view to display a button to enroll.