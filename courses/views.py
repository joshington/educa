from django.db.models import Count
from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic.list import ListView
from .models import Course,Subject
from students.forms import CourseEnrollForm




from django.views.generic.base import TemplateResponseMixin,View
from .forms import ModuleFormSet

from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView,UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
# Create your views here.

class ManageCourseListView(ListView):
    model=Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs=super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)

#it inherits from django's generic ListView.we override the get_queryset() mthd  of the view
#to retrieve only courses created by the current user.to prevent users from editing,updating,
#or deleting courses they didnt create,we will also need to override the get_queryset() in the
#create,update,and delete views, its recommended to use mixins


#===mixins are aspecial kind of multiple inheritance for aclass,u can use them to provide
#common discrete functionality that,added  to other mixins allows u to define the behavior of aclass
#there 2 main situations to use mixins
# You want to provide multiple optional features for a class
# You want to use a particular feature in several classes
# We are going to create a mixin class that includes a common
# behavior and use it for the course's views.

class OwnerMixin(object):
    def get_queryset(self):
        qs=super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)
#we override this mthd to automatically set the current user in the owner attribute of the
#object being saved,by doing so,we set the owner for an object automatically when it is saved

class OwnerCourseMixin(OwnerMixin,LoginRequiredMixin):
    model=Course
    fields=['subject','title','slug','overview']
    success_url = reverse_lazy('manage_course_list')

class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields=['subject','title','slug','overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'

class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name='courses/manage/course/list.html'

class CourseCreateView(PermissionRequiredMixin,OwnerCourseEditMixin,CreateView):
    permission_required='courses.add_course'

class CourseUpdateView(PermissionRequiredMixin,OwnerCourseEditMixin,UpdateView):
    permission_required='courses.change_course'
    #allows editing an existing Course object.it inherits from OwnerCourseEditMixin and
    #UpdateView

class CourseDeleteView(PermissionRequiredMixin,OwnerCourseMixin,DeleteView):
    template_name='courses/manage/course/delete.html'
    success_url=reverse_lazy('manage_course_list')
    permission_required='courses.delete_course'

#get_queryset()=this mthd is used by the views to get the base queryset our mixin will 
#override this methodto filter objects by the owner attribute to retrieve objects
#that belong to the current user(request.user)

#OwnerEditMixin=>

#===PermissionRequiredMixin checks that the user accessing the view has the 
#permission specified in the permiss permission specifid in the prmission_required attribute
#our views are now only accessible to users that have proper permissions

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    #View=>the basic class-based view provided by django
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    #this mthd is to avoid repeating the code to build the formset.we create a ModuleFormSet
    #object for the given Course object with optional data

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)
    #this mthd is provided by the View class, it takes an HTTP request and its params
    #and attempts to delegate to alowercase mthd that matches the HTTP mthd used.
    #get_object_or_404 shortcut function to get the Course object for the given id parameter
    #that belongs to the current user,we  include this code in the dispatch() mthd because
    #we need to retrieve the course for both GET and POST request.we save it in the course
    #attribute of the view to make it accessible to other mthds

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course':self.course, 'formset':formset})
        #we build an empty ModuleFormSet formset and render it to the template together
        #with the current Course object using the render_to_response () mthd provided
        #by TemplateResponseMixin
    
    def post(self, request,*args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course':self.course, 'formset':formset})

#the above view handles the formset to add, update,update and delete modules for aspecific course
#this view inherits from the following mixins and views
#TemplateResponseMixin- mixin takes charge of rendering templates and  returning an 
#HTTP response.it requires a temp[late_name attribute that indicates the template to be
#rendered and provides the render_to _response() mthd to pass it acontext and 
# render the template 


#===adding content to modules,since we have four different types of content;text,video,image,
#and file, we can consider four different views to create content,one for each model
#yet we are going to take amore generic approach and create aview that handles creatingor
#updating objects of any content model


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module=None
    model=None
    obj=None
    template_name='courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text','video','image','file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
    #in this mthd we check that the given model name is one of the four content modelS:Text,Video,
    #Image or File, then we use django's apps module to obtain the actual class for the given model
    #name.if the given model name is not one of the valid ones,we return None
    
    def get_form(self, model, *args, **kwargs):
        Form=modelform_factory(model, exclude=['owner', 'order','created','updated'])
        return Form(*args, **kwargs)
    #we build, adynamic form using the modelform_factory() function of the form's framework,since we
    #are going to build aform for the Text,Video,Image,and File models,we use the exclude parameter
    #to specify the common fields to exclude from the form and let all other attributes be included
    #automatically,thus we dont have to know which fields to include depending on the model



#the following will allow us to create and update contents of different models.this view

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,id=module_id,course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,id=id, owner=request.user)
        return super(ContentCreateUpdateView,self).dispatch(request,module_id, model_name,id)
    #it receives the following url parameters and stores the corresponding module,model,and
    #content object as class attributes

    #module_id=the id for the modue that the content is/will be associated with
    #model_name+> the model name of the content to create/update
    #id=>the id of the object that is being updated.its None to create new objects

    #this view allows us to create and update contents of different models.it defines the
    #following mthds
    #get_model()=.
    
    def get(self, request, module_id, model_name, id=None):
        form=self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form':form, 'object':self.obj})
    #executed when a GET request is received.we build the model form for the Text,Video,Image
    #or File instance that is being updated.otherwise pass no instance to create a new object,
    #since self.obj is None if no ID is provided.



    def post(self,request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, 
            data=request.POST,files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                #new content
                Content.objects.create(module=self.module,item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'fomr':form, 'object':self.obj})
    #executed when apost request is received.we build the modelform passing any submitted
    #data and files to it.then we validate it.if form is valid, we create a new object
    #assign request.user as its owner before saving it to the db.we check for the id
    #parameter, if no ID is provided,we know user is creating anew object instead of
    #updating an existing one.if this is anew object,we create a Content object for the
    #given module and associate the new content to it


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,id=id,module__course__owner=request.user)
        module=content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

#view to display all modules for a course and list contents for aspecific module.
#retrieves the Content object with the given ID,it delets the related Text,Video,Image
#or File object, and finally it deletes the Content object and redirects the user to the
#module_content_list URL to list  the other contents of the module

#===viwe to display all modules for acourse and list contents for aspecific module

class ModuleContentListView(TemplateResponseMixin,View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id,course__owner=request.user)
        return self.render_to_response({'module': module})




# We need to provide a simple way to reorder course modules and
# their contents. We will use a JavaScript drag-n-drop widget to let
# our users reorder the modules of a course by dragging them. When
# users finish dragging a module, we will launch an asynchronous
# request (AJAX) to store the new module order.#

#need aview that receives the new order of modules' ID encoded in JSON
# CSrfExemptMixin= to avoid checking the CSRF token in the POST requests.we need this
#to perform ajax post requests without having to generate a csrf_token.


from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved':'OK'})

#view to order a module's contents

class ContentOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved':'OK'})


#here we are to create public views for displaying course info
#build astudent registration system
#manage student enrollment in courses
#render diverse course contents
#cache content using the cache framework

#start by creating acourse catalog for students to browse existing courses and be able to
#enroll in them

#==course catalog => list all available courses,optionally filtered by subject,display
#==asingle course overview

class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self,request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))

        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response({'subjects':subjects,
            'subject':subject,'courses':courses})
    #here we retrieve all subjects,including the total number of courses for each of them
    #we use the ORM's annotate mthd with the Count() aggregation function to include
    #the total number of courses for each subject
    #we retrieve all avilable courses, includng the total number of modules contained in
    #each course.
    #if asubject slug URL parameter is given,we retrieve the corresponding subject object
    #and we limit the query to the courses that belong to the given subject
    #we use the render_to_respone mthd provided by TemplateResponseMixin to render the
    #objects to atemplate and return an HTTP response

class CourseDetailView(DetailView):
    model =Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView,self).get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context

#we use the get_context_data() mthd to include the enrollment form in the context for rendering
#the templates,we initialize the hidden course field of the from with the current Course object
#so that it can be submitted direclty.