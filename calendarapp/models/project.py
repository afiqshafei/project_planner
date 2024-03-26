from django.db import models
from accounts.models import User

# class Project(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     start_date = models.DateField()
#     end_date = models.DateField()

#     def __str__(self):
#         return self.title

class ProjectTemplate(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.DurationField()

    def __str__(self):
        return self.title

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)    
    start_date = models.DateField()
    template = models.ForeignKey(ProjectTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    save_as_template = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    days_prior = models.IntegerField()
    # duration = models.DurationField()
    # duration = models.IntegerField(label='Number of Days', min_value=0)
    duration = models.IntegerField()
    is_actionable = models.BooleanField(default=True)
    email_notification = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
# added for the template
class TaskTemplate(models.Model):
    template = models.ForeignKey(ProjectTemplate, related_name='task_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    days_prior = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return self.name