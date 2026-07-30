from django import forms
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    pass