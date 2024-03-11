from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from calendarapp.models import Event
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from accounts.forms import UserProfileUpdateForm
from django.urls import reverse_lazy

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

