from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_comments_xtd.forms import XtdCommentForm
from django_comments_xtd.models import TmpXtdComment
from django import forms
from .models import TkComment
from martor.fields import MartorFormField
from martor.widgets import AdminMartorWidget

class TkCommentForm(XtdCommentForm):
    """Extended comment form"""

    comment_anonymous = forms.BooleanField(required=False)
    def get_comment_create_data(self, site_id=None):
        data = super(TkCommentForm, self).get_comment_create_data()
        comment_status = self.cleaned_data.get('comment_anonymous')
        print("status", comment_status)

        data.update({'comment_anonymous': comment_status,})
        return data

class CommentForm(forms.ModelForm):
    """Comment form used to edit comments."""
    class Meta:
        model = TkComment
        fields = ('comment',)
