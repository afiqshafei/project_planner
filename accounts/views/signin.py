from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.forms import SignInForm
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileUpdateForm


class SignInView(View):
    """ User registration view """

    template_name = "accounts/signin.html"
    form_class = SignInForm

    def get(self, request, *args, **kwargs):
        forms = self.form_class()
        context = {"form": forms}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            email = forms.cleaned_data["email"]
            password = forms.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect("calendarapp:calendar")
        context = {"form": forms}
        return render(request, self.template_name, context)
    
    # Just added
    
    @login_required
    def update_profile(request):
        if request.method == 'POST':
            form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile_view')  # Replace 'profile_view' with the name of the URL where the user views their profile
        else:
            form = UserProfileUpdateForm(instance=request.user)

        return render(request, 'accounts/edit_profile.html', {'form': form})
