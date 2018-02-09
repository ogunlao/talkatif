from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_comments_xtd.forms import XtdCommentForm
from django_comments_xtd.models import TmpXtdComment

class TkCommentForm(XtdCommentForm):
    COMMENT_CHOICES = (
        ('BE YOURSELF', 'BE YOURSELF'),
        ('BE ANONYMOUS', 'BE ANONYMOUS'),
        )
    comment_anonymous = forms.ChoiceField(choices=COMMENT_CHOICES)

    def get_comment_create_data(self, site_id=None):
        data = super(TkCommentForm, self).get_comment_create_data()
        comment_status = self.cleaned_data.get('comment_anonymous')
        print("status", comment_status)

        data.update({'comment_anonymous': comment_status,})
        return data