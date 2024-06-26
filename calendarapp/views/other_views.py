from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from calendarapp.models import EventMember, Event
from calendarapp.utils import Calendar
from calendarapp.forms import EventForm, AddMemberForm
from calendarapp.models.project import Project, Task, ProjectTemplate, TaskTemplate
from calendarapp.forms import ProjectForm, TaskForm


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(LoginRequiredMixin, generic.ListView):
    login_url = "accounts:signin"
    model = Event
    template_name = "calendarapp:calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        # just added
        # context['project_templates'] = ProjectTemplate.objects.filter(user=self.request.user)

        return context


@login_required(login_url="signup")
def create_event(request):
    form = EventForm(request.POST or None)
    if request.POST and form.is_valid():
        title = form.cleaned_data["title"]
        description = form.cleaned_data["description"]
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        Event.objects.get_or_create(
            user=request.user,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
        )
        return HttpResponseRedirect(reverse("calendarapp:calendar"))
    return render(request, "event.html", {"form": form})

# def add_project(request):
#     form = ProjectForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#          title = form.cleaned_data["title"]       
#          start_date = form.cleaned_data["start_date"]   
#          save_as_template = form.cleaned_data["save_as_template"]  
#          Project.objects.get_or_create(
#              user = request.user,
#              title=title,            
#             start_date=start_date,
#             save_as_template = save_as_template,
#          )
         
#          return redirect('add_task')

@login_required
def add_project(request):
    form = ProjectForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.user = request.user
        project.save()
        template = form.cleaned_data.get('template')
        if template:
            # Copy tasks from the template
            for task_template in template.task_templates.all():
                Task.objects.create(
                    project=project,
                    name=task_template.name,
                    days_prior=task_template.days_prior,
                    duration=task_template.duration
                )
        # return redirect('list_user_projects_and_tasks')  # Adjust the redirection to your needs
        return redirect('add_task')
    return render(request, "add_project.html", {"form": form})

@login_required
def create_template_from_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project_template = ProjectTemplate.objects.create(
        title=project.title + " Template",
        user=request.user,
        # duration=(project.end_date - project.start_date) if project.end_date else None
    )
    # Copy tasks to TaskTemplate
    for task in project.tasks.all():
        TaskTemplate.objects.create(
            template=project_template,
            name=task.name,
            days_prior=task.days_prior,
            duration=task.duration
        )
    project.save_as_template = True
    project.save()
    # return redirect('template_list')  # Redirect to the template list or confirmation page
    return redirect('list_user_projects_and_tasks')



@login_required
def save_project_as_template(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        # Create a new ProjectTemplate
        project_template = ProjectTemplate.objects.create(
            title=project.title + " Template",
            user=request.user,
        )
        # Copy tasks to TaskTemplate
        for task in project.tasks.all():
            TaskTemplate.objects.create(
                template=project_template,
                name=task.name,
                days_prior=task.days_prior,
                duration=task.duration,
            )
        messages.success(request, "Project saved as template successfully.")
        return redirect('list_user_projects_and_tasks')
    else:
        messages.error(request, "Only POST method is accepted.")
        return redirect('list_user_projects_and_tasks')

@login_required
def create_project_from_template(request):
    if request.method == "POST":
        template_id = request.POST.get('template_id')
        project_name = request.POST.get('project_name')
        start_date = request.POST.get('start_date')

        # Fetch the selected template
        project_template = get_object_or_404(ProjectTemplate, id=template_id)

        # Create a new project
        project = Project.objects.create(
            user=request.user,
            title=project_name,
            start_date=start_date
        )

        # Copy tasks from the template
        for task_template in project_template.task_templates.all():
            Task.objects.create(
                project=project,
                name=task_template.name,
                days_prior=task_template.days_prior,
                duration=task_template.duration
            )

        messages.success(request, "New project created from template successfully.")
        return redirect('list_user_projects_and_tasks')

    # return redirect("add_project.html")  # Redirect to the form if not POST or invalid form
    return redirect("calendar")

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('list_user_projects_and_tasks')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'edit_project.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('list_user_projects_and_tasks')
    return render(request, 'delete_project.html', {'project': project})

    

# def template_list(request):
#     templates = Project.objects.filter(is_template=True)    
#     return render(request, 'project/template_list.html', {'templates': templates})

@login_required
def list_user_projects_and_tasks(request):    
    user_projects = Project.objects.filter(user=request.user).prefetch_related('tasks')
    # project_templates = ProjectTemplate.objects.filter(user=request.user)
    for project in user_projects:
        for task in project.tasks.all():
            task.start_date = project.start_date - timedelta(days=task.days_prior)

    return render(request, 'user_projects_and_tasks.html', {'user_projects': user_projects})
    # return render(request, 'calendarapp/calendar.html', {
    #     'user_projects': user_projects,
    #     'project_templates': project_templates,
    # })

@login_required
def templates_data(request):
    # project_templates = ProjectTemplate.objects.all()
    project_templates = ProjectTemplate.objects.filter(user=request.user)
    # print(project_templates)

    context = {        
        'project_templates' : project_templates,
    }

    print('Hello')

    return render(request, 'calendarapp/calendar.html', context)
    # return render(request, 'template_data.html', context)


@login_required
def toggle_task_completion(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__user=request.user)
    task.is_actionable = not task.is_actionable
    task.save()
    return redirect('list_user_projects_and_tasks')

# added for the template
# @login_required
# def create_project_from_template(request, project_id):
# # def create_template_from_project(request, project_id):
#     project = get_object_or_404(Project, id=project_id, user=request.user)
#     if request.method == 'POST':
#         # Create a new ProjectTemplate
#         project_template = ProjectTemplate.objects.create(
#             title=project.title + " Template",
#             user=request.user,
#             # duration=project.end_date - project.start_date
#         )
#         # Copy tasks to TaskTemplate
#         for task in project.tasks.all():
#             TaskTemplate.objects.create(
#                 template=project_template,
#                 name=task.name,
#                 days_prior=task.days_prior,
#                 duration=task.duration
#             )
#         # return redirect('list_templates')  # Redirect to a page where user can view all their templates
#         return redirect('list_user_projects_and_tasks')
    
#     return render(request, 'create_template_from_project.html', {'project': project})
#     return redirect("add_project.html")

@login_required
def add_task(request):
    form = TaskForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            project = form.cleaned_data["project"]
            name = form.cleaned_data["name"]
            days_prior = form.cleaned_data["days_prior"]
            duration = form.cleaned_data["duration"]
            is_actionable = form.cleaned_data["is_actionable"]
            email_notification = form.cleaned_data["email_notification"]

            Task.objects.get_or_create(
                project=project,
                name=name,
                days_prior=days_prior,
                duration=duration,
                is_actionable=is_actionable,
                email_notification=email_notification,
            )
            if request.POST.get('submit') == 'save_add_another':
                return redirect('add_task')  # Redirects to the same page for a new form
            elif request.POST.get('submit') == 'save_continue':                
                return redirect('list_user_projects_and_tasks')      
            else:                
                return redirect('list_user_projects_and_tasks')
        else:
            print(form.errors)

        return HttpResponseRedirect(reverse("calendarapp:calendar"))  
    return render(request, "add_task.html", {"form": form})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('list_user_projects_and_tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('list_user_projects_and_tasks')
    return render(request, 'delete_task.html', {'task': task})



# To display project/task on calendar
@login_required
def calendar_view(request):
    projects = Project.objects.filter(user=request.user).prefetch_related('tasks')
    events = []

    for project in projects:        
        events.append({
            "title": project.title,
            "start": project.start_date.strftime("%Y-%m-%d"),
            "allDay": True
        })
        
        for task in project.tasks.all():
            task_date = project.start_date - timedelta(days=task.days_prior)
            events.append({
                "title": task.name,
                "start": task_date.strftime("%Y-%m-%d"),
                "allDay": True
            })
    
    events_json = json.dumps(events)
    
    return render(request, 'calendar.html', {'events_json': events_json})
    # context = {
    #     "events": json.dumps(events)  
    # }

    # return render(request, 'calendar.html', context)

class EventEdit(generic.UpdateView):
    model = Event
    fields = ["title", "description", "start_time", "end_time"]
    template_name = "event.html"


@login_required(login_url="signup")
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    eventmember = EventMember.objects.filter(event=event)
    context = {"event": event, "eventmember": eventmember}
    return render(request, "event-details.html", context)


def add_eventmember(request, event_id):
    forms = AddMemberForm()
    if request.method == "POST":
        forms = AddMemberForm(request.POST)
        if forms.is_valid():
            member = EventMember.objects.filter(event=event_id)
            event = Event.objects.get(id=event_id)
            if member.count() <= 9:
                user = forms.cleaned_data["user"]
                EventMember.objects.create(event=event, user=user)
                return redirect("calendarapp:calendar")
            else:
                print("--------------User limit exceed!-----------------")
    context = {"form": forms}
    return render(request, "add_member.html", context)


class EventMemberDeleteView(generic.DeleteView):
    model = EventMember
    template_name = "event_delete.html"
    success_url = reverse_lazy("calendarapp:calendar")

class CalendarViewNew(LoginRequiredMixin, generic.View):
    login_url = "accounts:signin"
    template_name = "calendarapp/calendar.html"
    form_class = EventForm

    def get(self, request, *args, **kwargs):
        forms = self.form_class()
        project_templates = ProjectTemplate.objects.filter(user=request.user)
        events = Event.objects.get_all_events(user=request.user)
        events_month = Event.objects.get_running_events(user=request.user)
        event_list = []
        # start: '2020-09-16T16:00:00'
        for event in events:
            event_list.append(
                {   "id": event.id,
                    "title": event.title,
                    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "description": event.description,
                }
            )
        
        context = {"form": forms, "events": event_list,
                   "events_month": events_month,
                   "project_templates":project_templates,
                   }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            form = forms.save(commit=False)
            form.user = request.user
            form.save()
            return redirect("calendarapp:calendar")
        context = {"form": forms}
        return render(request, self.template_name, context)



def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'message': 'Event sucess delete.'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)

def next_week(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.start_time += timedelta(days=7)
        next.end_time += timedelta(days=7)
        next.save()
        return JsonResponse({'message': 'Sucess!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)

def next_day(request, event_id):

    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.start_time += timedelta(days=1)
        next.end_time += timedelta(days=1)
        next.save()
        return JsonResponse({'message': 'Sucess!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)
    

