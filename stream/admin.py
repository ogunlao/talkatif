from django.contrib import admin

# Register your models here.
from .models import PostDebate, Profile, Participation, Suggest, Votes, \
            Notifyme, Stat, Scores, Badge, TrackedPost, Attachment, PostDebater

admin.site.register(Participation)

admin.site.register(Suggest)

class AttachmentInline(admin.StackedInline):
    model = Attachment
    #can_delete = False
    verbose_name_plural = 'Attached Images'
    fk_name = 'post'

@admin.register(PostDebate)
class PostDebateAdmin(admin.ModelAdmin):
    inlines = (AttachmentInline, )
    list_display = ('title', 'winner', 'slug', 'get_likes','show', 'debate_notification','debate_category', 'allow_comments', 'status', 'author', 'created', 'begin', 'end', 'vote_starts', 'stats_updated',)
    list_filter = ('created', 'debate_category',)
    search_fields = ('title', 'summary',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created'

    def get_likes(self, instance):
        return instance.total_likes
    get_likes.short_description = 'Total Likes'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'tags', 'debate_category', 'summary', #'tags',
            'author', )
        }),
        ('Ticks', {
            'fields': ('show', 'stats_updated', 'winner_updated', 'debate_notification',)
        }),
        ('Dates', {
            'fields': ('begin', 'end', 'vote_starts')
        }),
        ('Participants', {
            'fields': ('supporting_debaters', 'opposing_debaters', 'moderator', 'judges',)
        }),
    )

@admin.register(Scores)
class ScoresAdmin(admin.ModelAdmin):
    list_display = ('post', 'supporting_score', 'opposing_score', 'supporting_vote', 'opposing_vote','observation',)

@admin.register(PostDebater)
class PostDebaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'debate_position', 'approval_status',)

@admin.register(TrackedPost)
class TrackedPostAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip', 'user',)

@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('post', 'person', 'supported', 'opposed', 'moderated', 'judged', 'won', 'lost', 'drew',)
    list_filter = ()
    search_fields = ('post', 'person',)

@admin.register(Votes)
class VotesAdmin(admin.ModelAdmin):
    list_display = ('post', 'voter', 'support', 'oppose',)

@admin.register(Notifyme)
class NotifymeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user_notify', 'notified', )
    list_filter = ('post', 'user_notify',)
    search_fields = ('post', 'user_notify',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','rank', 'category' )

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_specialization')
    list_select_related = ('profile', )

    def get_specialization(self, instance):
        return instance.profile.specialization
    get_specialization.short_description = 'specialization'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
