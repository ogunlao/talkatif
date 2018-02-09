from django.contrib import admin

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_comments_xtd.admin import XtdCommentsAdmin
from tkcomments.models import TkComment


class TkCommentAdmin(XtdCommentsAdmin):
    list_display = ('thread_level',  'cid', 'name', 'comment_anonymous','anonymous_user','content_type',
                    'object_pk', 'submit_date', 'followup', 'is_public',
                    'is_removed')
    list_display_links = ('cid',)
    fieldsets = (
        (None,          {'fields': ('content_type', 'object_pk', 'site', 'comment_anonymous','anonymous_user')}),
        (_('Content'),  {'fields': ('user', 'user_name', 'user_email',
                                    'user_url', 'comment', 'followup')}),
        (_('Metadata'), {'fields': ('submit_date', 'ip_address',
                                    'is_public', 'is_removed')}),
    )

admin.site.register(TkComment, TkCommentAdmin)
