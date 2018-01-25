from .models import PostDebate, Profile, Scores, Attachment
from django import forms
from django.contrib.auth.models import User
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries #country dropdown
from django.contrib.auth.hashers import make_password #used to hash passwords
from multiupload.fields import MultiImageField




class PostDebateForm(forms.ModelForm):
    attachment = MultiImageField(min_num=0, max_num=2, max_file_size=1024*1024*5, required = False)
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
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Re-enter Password')
    city = forms.CharField(max_length=100, label='Your Current City')
    country = LazyTypedChoiceField(choices=countries)
    specialization = forms.CharField(label='Specialization', help_text="e.g. Practicing Lawyer, \
                        Programmer, Business Man, Political Activist")

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2

    def save(self, request):
        # Save your user
        user = User()
        profile = Profile()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        user.password = make_password(self.clean_password2())
        #set_password(self.cleaned_data["password1"])

        import random
        user.username = user.first_name + str(random.randint(0,99))

        def clean_password2(self):
            password1 = self.cleaned_data.get('password1')
            password2 = self.cleaned_data.get('password2')

            if not password2:
                raise forms.ValidationError("You must confirm your password")
            if password1 != password2:
                raise forms.ValidationError("Your passwords do not match")
            return password2

        user.save()

        profile.user = user
        profile.city = self.cleaned_data['city']
        profile.country = self.cleaned_data['country']
        profile.specialization = self.cleaned_data['specialization']
        profile.save()

        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)

class ScoresForm(forms.ModelForm):
    class Meta:
        model = Scores
        exclude = ('post',)
        #fields = ('supporting_score', 'opposing_score', 'observation')

class ModeratorForm(forms.ModelForm):
    class Meta:
        model = PostDebate
        fields = ('begin', 'end', 'vote_starts')
