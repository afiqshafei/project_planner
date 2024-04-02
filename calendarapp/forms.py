from django.forms import ModelForm, DateInput
from calendarapp.models import Event, EventMember
from django import forms
from datetime import timedelta
from calendarapp.models.project import Project, Task, ProjectTemplate



class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_time", "end_time"]
        # datetime-local is a HTML5 input type
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": ""}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter event description",
                }
            ),
            "start_time": DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = EventMember
        fields = ["user"]       


        
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'start_date', 'template', 'save_as_template']        
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Project Name"}            
            ),
            
             "start_date": DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            # newly added for the template
            "template": forms.Select(
                attrs={"class":"form-control"}
            ),
            "save_as_template": forms.CheckboxInput(
                attrs={"class": 'form-check-input'}
            ),
          
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['template'].queryset = ProjectTemplate.objects.filter(user=user)

class TaskForm(forms.ModelForm):
    # duration_in_days = forms.IntegerField(
    #     widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Duration in days"}),
    #     label='Duration (in days)',
    #     required=False,
    # )
    class Meta:
        model = Task
        fields = ['project','name', 'days_prior', 'duration', 'is_actionable', 'email_notification']
        # newly added la
        widgets = {
            "project": forms.Select(
                attrs={"class": "form-control"}
                                    ),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Task name"}
            
            ),

            "days_prior": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Days prior "}
            ),
            
             "duration":forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Duration in days"}
            ),
             "is_actionable": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "email_notification": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['project'].queryset = Project.objects.filter(user=user)

 

    