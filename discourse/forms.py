from debate.models import PostDebate
from .models import Post
from django import forms
from django.contrib.auth.models import User
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries #country dropdown
from django.contrib.auth.hashers import make_password #used to hash passwords

class PostDebateForm(forms.ModelForm):
    class Meta:
        model = PostDebate
        fields = ('title', 'summary', 'tags','debate_category', 'allow_comments',\
                    'begin' , 'end', 'vote_starts', 'supporting_debaters', 'opposing_debaters',\
                    'moderator', 'judges')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'summary', 'tags',)
