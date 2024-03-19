from django.views.generic import View, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from calendarapp.models import Event
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from accounts.forms import UserProfileUpdateForm
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from calendarapp.forms import ProjectForm, TaskForm
from django.http import HttpResponseRedirect
from calendarapp.models.project import Project, Task

class DashboardView(LoginRequiredMixin, View):
    login_url = "accounts:signin"
    template_name = "calendarapp/dashboard.html"

    def get(self, request, *args, **kwargs):
        events = Event.objects.get_all_events(user=request.user)
        running_events = Event.objects.get_running_events(user=request.user)
        latest_events = Event.objects.filter(user=request.user).order_by("-id")[:10]
        context = {
            "total_event": events.count(),
            "running_events": running_events,
            "latest_events": latest_events,
        }
        return render(request, self.template_name, context)
    
    # just added
    # @login_required
    # def profile(request):
    #     return render(request, 'profile.html')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/update_profile.html'   
    success_url = reverse_lazy('dashboard')  # Redirect to the profile page after a successful update

    def get_object(self):
        return self.request.user 
    
    def form_valid(self, form):
        response = super(UpdateProfileView, self).form_valid(form)
        messages.success(self.request, 'Your profile has been updated.') 
        return response


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'calendarapp/create_new_project.html'
    success_url = reverse_lazy('calendar')

    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['task_formset'] = TaskFormSet(self.request.POST)
        else:
            context['task_formset'] = TaskFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        task_formset = context['task_formset']
        if task_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            task_formset.instance = self.object
            tasks = task_formset.save(commit=False)
            
            # Logic to handle email notifications...
            
            for task in tasks:
                task.save()
            
            # Add logic here if you need to perform additional steps after saving the project
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(ProjectCreateView, self).form_invalid(form)

    def get_success_url(self):
        # Here you can add logic to determine the success URL dynamically
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

TaskFormSet = inlineformset_factory(Project, Task, form=TaskForm, extra=1, can_delete=True)