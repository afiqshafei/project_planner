from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from accounts.models import User


class SignInForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="First Name"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Last Name"
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {"email": forms.EmailInput(attrs={"class": "form-control"})}

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password didn't match!")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]        
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

