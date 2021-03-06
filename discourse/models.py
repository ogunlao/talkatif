from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.conf import settings
from django.core.urlresolvers import reverse
from django_countries.fields import CountryField #For Profile


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(show='True')

class Post(models.Model):
    objects = models.Manager() # The default manager.
    published = PublishedManager() # Our custom manager.
    title = models.CharField(max_length=500, help_text="Give a clear title for the post")
    slug = models.SlugField(max_length=250, unique=True)
    show = models.BooleanField('Post Enabled/Disabed', default=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name='author', default = User)
    summary = models.TextField('What are we discussing today?')
    allow_comments = models.BooleanField('allow comments', default=True)
    tags = TaggableManager(blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes_post')

    count = models.PositiveIntegerField(default = 0)

    @property
    def total_likes(self):
        """
        Likes for the debate
        :return: Integer: Likes for the debate post
        """
        return self.likes.count()

    def save(self):
          if not self.id:
              # Newly created object, so set slug
              self.slug = slugify(self.title)

          super(Post, self).save()

    def get_absolute_url(self):
        return reverse('discourse:post_detail', args=[self.pk, self.slug])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

class TrackedPost(models.Model):
    """
    Model used to track total unique visitors to a debate.
    """
    post = models.ForeignKey(Post)
    ip = models.CharField(max_length=16) #only accounting for ipv4
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name ="visits") #if you want to track logged in or anonymous

# Comment Moderation
from django_comments_xtd.moderation import moderator, SpamModerator
from discourse.badwords import badwords

class PostUserCommentModerator(SpamModerator):
    email_notification = True

    def moderate(self, comment, content_object, request):
        # Make a dictionary where the keys are the words of the message and
        # the values are their relative position in the message.
        def clean(word):
            ret = word
            if word.startswith('.') or word.startswith(','):
                ret = word[1:]
            if word.endswith('.') or word.endswith(','):
                ret = word[:-1]
            return ret

        lowcase_comment = comment.comment.lower()
        msg = dict([(clean(w), i)
                    for i, w in enumerate(lowcase_comment.split())])
        for badword in badwords:
            if isinstance(badword, str):
                if lowcase_comment.find(badword) > -1:
                    return True
            else:
                lastindex = -1
                for subword in badword:
                    if subword in msg:
                        if lastindex > -1:
                            if msg[subword] == (lastindex + 1):
                                lastindex = msg[subword]
                        else:
                            lastindex = msg[subword]
                    else:
                        break
                if msg.get(badword[-1]) and msg[badword[-1]] == lastindex:
                    return True
        return super(PostUserCommentModerator, self).moderate(comment,
                                                          content_object,
                                                          request)

moderator.register(Post, PostUserCommentModerator)
