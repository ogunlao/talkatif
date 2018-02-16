from django.contrib import admin
from django.db import models
from .models import Post
from martor.widgets import AdminMartorWidget

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'allow_comments', 'author', )
    list_filter = ('created', 'category',)
    search_fields = ('title', 'summary',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created'

    fieldsets = (
        (None, {
            'fields': ('title','slug', 'category', 'summary', 'tags','author' )
        }),
    )

class MarkdownPost(Post):
    """
    Custom admin to preview and edit postdebate in markdown.
    """
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }
    class Meta:
        proxy = True

admin.site.register(MarkdownPost, PostAdmin)
