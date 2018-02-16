from django.db import models

from django_comments_xtd.models import XtdComment
from django_comments_xtd.models import XtdCommentManager
from django.contrib.auth.models import User
from django.conf import settings

class TkComment(XtdComment):
    comment_anonymous = models.BooleanField('Is this comment an anonymous comment', default = False, blank = True, help_text="comment as anonymous")

    anonymous_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='anonymous_user')

    objects = XtdCommentManager()

    def save(self):
        if not self.id:
            if self.comment_anonymous == True:
                self.anonymous_user = self.user
                user = User.objects.get(username="AnonymousUser")
                self.user = user

        super(TkComment, self).save()
