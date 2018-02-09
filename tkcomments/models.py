from django.db import models

from django_comments_xtd.models import XtdComment
from django_comments_xtd.models import XtdCommentManager
from django.contrib.auth.models import User
from django.conf import settings

class TkComment(XtdComment):
    COMMENT_CHOICES = (
        ('BE YOURSELF', 'BE YOURSELF'),
        ('BE ANONYMOUS', 'BE ANONYMOUS'),
        )
    comment_anonymous = models.CharField('Is this comment an anonymous comment', max_length=12, null=True, choices=COMMENT_CHOICES, blank=True, help_text="comment as anonymous")
    anonymous_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='anonymous_user')

    objects = XtdCommentManager()

    def save(self):
        if not self.id:
            if self.comment_anonymous == "BE ANONYMOUS":
                self.anonymous_user = self.user
                user = User.objects.get(username="AnonymousUser")
                self.user = user

        super(TkComment, self).save()
