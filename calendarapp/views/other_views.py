from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from calendarapp.models import EventMember, Event
from calendarapp.utils import Calendar
from calendarapp.forms import EventForm, AddMemberForm
from calendarapp.models.project import Project, Task
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
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
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


def add_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
         title = form.cleaned_data["title"]       
         start_date = form.cleaned_data["start_date"]     
         Project.objects.get_or_create(
             user = request.user,
             title=title,            
            start_date=start_date,
         )
         return redirect('add_task')
        #  return HttpResponseRedirect(reverse("calendarapp:calendar"))           
          
    
    return render(request, "event.html", {"form": form})

@login_required
def list_user_projects_and_tasks(request):
    # Fetch all projects for the user with prefetch_related for efficiency
    user_projects = Project.objects.filter(user=request.user).prefetch_related('tasks')

    return render(request, 'user_projects_and_tasks.html', {'user_projects': user_projects})
    

# def add_task(request):
#     form = TaskForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#          title = form.cleaned_data["title"]
#         #  name = form.cleaned_data["name"]
#          start_date = form.cleaned_data["start_date"]

#          Task.objects.get_or_create(
#              user = request.user,
#              title=title,            
#             start_date=start_date,
#          )
#          return HttpResponseRedirect(reverse("calendarapp:calendar"))      
#         #  return HttpResponseRedirect("reverse("add_task")")    
    
#     return render(request, "event.html", {"form": form})

@login_required
def add_task(request):
    form = TaskForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        project = form.cleaned_data["project"]
        name = form.cleaned_data["name"]
        duration = form.cleaned_data["duration"]
        is_actionable = form.cleaned_data["is_actionable"]
        email_notification = form.cleaned_data["email_notification"]

        Task.objects.get_or_create(
            project=project,
            name=name,
            duration=duration,
            is_actionable=is_actionable,
            email_notification=email_notification,
        )
        if 'save_add_another' in request.POST:
                return redirect('add_task')  # Redirects to the same page for a new form
        elif 'save_continue' in request.POST:
            return HttpResponseRedirect(reverse("calendarapp:calendar"))
            # return redirect('edit_task_url_name', pk=task.pk)  # Redirect to the edit page of the newly created task
        else:
            # return redirect('task_list_url_name')
            return HttpResponseRedirect(reverse("calendarapp:calendar"))

        return HttpResponseRedirect(reverse("calendarapp:calendar"))  
    return render(request, "add_task.html", {"form": form})






        


# def add_project(request):
#     if request.method == 'POST':
#         form = ProjectForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("calendarapp/calendar.html")

#     else:
#         form = ProjectForm()

#     return render(request, "calendarapp/calendar.html", {'form':form} )

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
                   "events_month": events_month}
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


# class ProjectCreateView(CreateView):
#     model = Project
#     form_class = ProjectForm
#     template_name = 'create_new_project.html'
#     success_url = reverse_lazy('calendar')

#     def get_context_data(self, **kwargs):
#         context = super(ProjectCreateView, self).get_context_data(**kwargs)
#         if self.request.POST:
#             context['task_formset'] = TaskFormSet(self.request.POST)
#         else:
#             context['task_formset'] = TaskFormSet()
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         task_formset = context['task_formset']
#         if task_formset.is_valid():
#             self.object = form.save(commit=False)
#             self.object.user = self.request.user
#             self.object.save()
#             task_formset.instance = self.object
#             tasks = task_formset.save(commit=False)
            
#             # Logic to handle email notifications...
            
#             for task in tasks:
#                 task.save()
            
#             # Add logic here if you need to perform additional steps after saving the project
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#             return super(ProjectCreateView, self).form_invalid(form)

#     def get_success_url(self):
#         # Here you can add logic to determine the success URL dynamically
#         return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

# TaskFormSet = inlineformset_factory(Project, Task, form=TaskForm, extra=1, can_delete=True)