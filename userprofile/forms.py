from django import forms
from django.contrib.auth.models import User
from django_countries import countries #country dropdown
from .models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email',)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)
