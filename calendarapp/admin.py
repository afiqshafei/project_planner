from django.contrib import admin
from calendarapp import models
from .models import project
from calendarapp.models.project import Project, Task


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    model = models.Event
    list_display = [
        "id",
        "title",
        "user",
        "is_active",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "is_deleted"]
    search_fields = ["title"]


@admin.register(models.EventMember)
class EventMemberAdmin(admin.ModelAdmin):
    model = models.EventMember
    list_display = ["id", "event", "user", "created_at", "updated_at"]
    list_filter = ["event"]


# admin.site.register(project.Project)

# admin.site.register(project.Task)


# @admin.register(project.Project)
# class ProjectAdmin(admin.ModelAdmin):
#     model = project.Project
#     list_display = ["id","title","user"]
    

# @admin.register(project.Task)
# class ProjectAdmin(admin.ModelAdmin):
#     model = project.Task
#     list_display = ["id", "name","project","duration"]
    

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "title","start_date", "user"]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "project", "days_prior", "duration"]

#     def formatted_duration(self, obj):
#         # Convert the duration to a string, assuming it's stored as a timedelta object
#         duration_days = obj.duration.days if obj.duration else 0
#         return "{} day(s)".format(duration_days)
    
#     formatted_duration.admin_order_field = 'duration'  # Allows sorting by the duration field
#     formatted_duration.short_description = 'Duration (days)'  # Column header for the admin interface
    
     