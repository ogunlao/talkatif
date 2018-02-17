from .models import PostDebate, Profile, Scores
from django import forms
from django.contrib.auth.models import User
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries #country dropdown
from django.contrib.auth.hashers import make_password #used to hash passwords
from django.contrib.auth import password_validation
import random

class PostDebateForm(forms.ModelForm):
    class Meta:
        model = PostDebate
        fields = ('title', 'summary', 'tags','debate_category',)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email',)

#To bypass the signup template of allauth
class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='First Name')
    last_name = forms.CharField(max_length=100, label='Last Name')
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'This email address has been already been registered.')
        return email

    def clean_password(self):
        validators = password_validation.get_default_password_validators()
        password = self.cleaned_data.get('password')
        print("pwd:", password)
        password_validation.validate_password(
            password,
            user=None,
            password_validators=validators,
            )
        return password

    def save(self, request):
        # Save your user
        user = User()
        profile = Profile()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user.password = make_password(password)
        username = user.first_name + str(random.randint(0,99))
        user.username = username.lower()
        user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)

class ScoresForm(forms.ModelForm):
    class Meta:
        model = Scores
        exclude = ('post', 'uploaded_by',)
        #fields = ('supporting_score', 'opposing_score', 'observation')

class ModeratorForm(forms.ModelForm):
    class Meta:
        model = PostDebate
        fields = ('begin', 'end', 'vote_starts')
