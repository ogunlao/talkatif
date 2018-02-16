from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.conf import settings
from django.core.urlresolvers import reverse
from martor.models import MartorField

# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(show='True')

class BlogPost(models.Model):
    objects = models.Manager() # The default manager.
    published = PublishedManager() # Our custom manager.
    title = models.CharField(max_length=250, help_text="Give a clear title for the post")
    slug = models.SlugField(max_length=100, unique=True)
    show = models.BooleanField('BlogPost Enabled/Disabed', default=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name='blogauthor', default = User)
    body = MartorField('Body of the blog post')
    allow_comments = models.BooleanField('allow comments', default=True)
    tags = TaggableManager(blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self):
          if not self.id:
              # Newly created object, so set slug
              self.slug = slugify(self.title)
          super(BlogPost, self).save()

    def get_absolute_url(self):
        return reverse('blog:blog_detail', args=[self.pk, self.slug])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title
