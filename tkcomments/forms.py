from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_comments_xtd.forms import XtdCommentForm
from django_comments_xtd.models import TmpXtdComment
from django import forms
from .models import TkComment
from markdownx.fields import MarkdownxFormField

class TkCommentForm(XtdCommentForm):
    """Extended comment form"""
    COMMENT_CHOICES = (
        ('B.Y', 'BE YOURSELF'),
        ('B.A', 'BE ANONYMOUS'),
        )
    comment_anonymous = forms.ChoiceField(choices=COMMENT_CHOICES)

    def get_comment_create_data(self, site_id=None):
        data = super(TkCommentForm, self).get_comment_create_data()
        comment_status = self.cleaned_data.get('comment_anonymous')
        print("status", comment_status)

        data.update({'comment_anonymous': comment_status,})
        return data

class CommentForm(forms.ModelForm):
    """Comment form used to edit comments."""
    comment = MarkdownxFormField()
    class Meta:
        model = TkComment
        fields = ('comment',)
