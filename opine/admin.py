from django.contrib import admin
from .models import Post, Attachment
# Register your models here.

class AttachmentInline(admin.StackedInline):
    model = Attachment
    #can_delete = False
    verbose_name_plural = 'Attached Images'
    fk_name = 'post'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (AttachmentInline, )
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
