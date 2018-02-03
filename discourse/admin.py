from django.contrib import admin
from .models import Post
from markdownx.admin import MarkdownxModelAdmin #used by markdown editor

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
    class Meta:
        proxy = True

admin.site.register(MarkdownPost, PostAdmin)
