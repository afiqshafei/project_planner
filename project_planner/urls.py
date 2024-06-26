"""project_planner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import DashboardView, ProfileView, UpdateProfileView, ProjectCreateView
from calendarapp.views import other_views
from calendarapp.views.other_views import CalendarView




urlpatterns = [
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("calendarapp.urls")),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('new_project/', ProjectCreateView.as_view(), name='new_project'),
    path('add_project/', other_views.add_project, name='add_project'),
    path('add_project/add_task', other_views.add_task, name="add_task"),    
    path('edit_project/<int:project_id>/', other_views.edit_project, name='edit_project'),
    path('delete_project/<int:project_id>/', other_views.delete_project, name='delete_project'),
    path('projects/', other_views.list_user_projects_and_tasks, name='list_user_projects_and_tasks'),
    path('projects/add_task/<int:project_id>/', other_views.add_task, name='add_task'),
    path('projects/edit_task/<int:task_id>/', other_views.edit_task, name='edit_task'),
    path('projects/delete_task/<int:task_id>/', other_views.delete_task, name='delete_task'),
    path('tasks/toggle/<int:task_id>/', other_views.toggle_task_completion, name='toggle_task_completion'),
    path('create_project_from_template/', other_views.create_project_from_template, name='create_project_from_template'),
    path('projects/add/', other_views.add_project, name='add_project'),
    # path('projects/<int:project_id>/save_as_template/', other_views.create_template_from_project, name='create_template_from_project'),
    # path('calendarView/', CalendarView.as_view, name='calendarView'),
    path('data/', other_views.templates_data, name='templates_data'),
    path('project/<int:project_id>/save_as_template/', other_views.save_project_as_template, name='save_project_as_template'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)