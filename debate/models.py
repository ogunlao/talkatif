from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.conf import settings
from django.core.urlresolvers import reverse
from django_countries.fields import CountryField #For Profile
from django.core.validators import MaxValueValidator, MinValueValidator

#versatile image imports
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.placeholder import OnDiscPlaceholderImage
import os

#For comment moderation
from django_comments_xtd.moderation import moderator, SpamModerator
from debate.badwords import badwords

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(show='True')

class PostDebate(models.Model):
    objects = models.Manager() # The default manager.
    published = PublishedManager() # Our custom manager.
    STATUS_CHOICES = (
        ('st', 'started'),
        ('end', 'ended'),
        )

    DEBATE_CATEGORY = (
        ('open', 'open'),
        ('closed', 'closed'),
        )
    WINNER = (
        ('supporting', 'Supporting Team'),
        ('opposing', 'Opposing Team'),
        ('draw', 'It was a tie'),
        ('InProgress', 'In Progress'),
        )
    title = models.CharField(max_length=500, help_text="Title of Debate")
    slug = models.SlugField(max_length=250, unique_for_date='created')
    show = models.BooleanField('Can debate be viewed online ?', default=True)
    debate_category = models.CharField(max_length=6, choices=DEBATE_CATEGORY, default='open')
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='st')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name='suggested_post')
    summary = models.TextField('What is your inspiration for the debate?', max_length=1000, help_text="Enter a brief summary. <a href='http://commonmark.org/help/' target='_blank'>Markdown supported<a/>")
    allow_comments = models.BooleanField('allow comments', default=True)
    tags = TaggableManager()
    begin = models.DateTimeField(null=True, blank = True)
    end = models.DateTimeField(null=True, blank = True)
    vote_starts = models.DateTimeField(null=True, blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    supporting_debaters = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, \
                    help_text="Select the supporting team",  related_name='supporting_team')
    opposing_debaters = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, \
                    help_text="Select the opposing team",related_name='opposing_team')
    moderator = models.ManyToManyField(settings.AUTH_USER_MODEL, \
                    help_text="Select moderators", related_name='debate_moderator')
    judges = models.ManyToManyField(settings.AUTH_USER_MODEL, \
                    help_text="Select judges", blank=True, related_name='judge_team')
    stats_updated = models.BooleanField('Has Statistics been updated', default=False)
    winner_updated = models.BooleanField('Has winner been declared', default=False)
    debate_notification = models.BooleanField('Has debaters, moderators and judges been notified', default=False)

    winner = models.CharField(max_length=10, blank=True, null=True, default = 'InProgress', choices=WINNER)
    count = models.PositiveIntegerField(default = 0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes')

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

          super(PostDebate, self).save()

    def get_absolute_url(self):
        return reverse('debate:debate_detail', args=[self.debate_category, self.pk, self.slug])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

class Attachment(models.Model):
    post = models.ForeignKey(PostDebate, related_name="attachment")
    file = VersatileImageField(
        'Image Attachments', blank=True, null=True,
        upload_to='attachments/debate', help_text="Add Pictures"
    )

    #file = models.FileField(upload_to='attachments/debate', help_text="Attach images to post. 2 max")
    def __str__(self):
        return self.file.name

class Stat(models.Model):
    """
    Model for updating statistics of each user
    """
    post = models.ForeignKey(PostDebate)
    person = models.ForeignKey(User)
    supported = models.BooleanField(default = False)
    opposed = models.BooleanField(default = False)
    moderated = models.BooleanField(default = False)
    judged = models.BooleanField(default = False)
    won = models.BooleanField(default = False)
    lost = models.BooleanField(default = False)
    drew = models.BooleanField(default = False)

class Votes(models.Model):
    """
    Model for capturing user votes for each debate.
    """
    post = models.ForeignKey(PostDebate)
    voter  = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name='user')
    support = models.NullBooleanField(default = False)
    oppose = models.NullBooleanField(default= False)
    voting_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Votes'

class Notifyme(models.Model):
    """
    Model used to notify followers when debate starts.
    """
    post = models.ForeignKey(PostDebate)
    user_notify = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name='user_to_nofify')
    notified = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = 'Notify Me'

class Scores(models.Model):
    """
    Model for judges to score debate
    """
    post = models.ForeignKey(PostDebate)
    #A judhe can assign a negative score if deemed fit
    supporting_score = models.SmallIntegerField(default=0, validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ], blank = True, help_text="Score for Supporting Side on a scale of 10")
    opposing_score = models.SmallIntegerField(default=0, validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ], blank = True, help_text="Score for Opposing Side on a scale of 10")
    highest_score = models.PositiveSmallIntegerField(default=10,blank = True, help_text="Highest Possible Score Possible")
    observation = models.TextField(max_length=1000, null=True, blank = True, help_text="If anomalies observed or comments, write here")

    supporting_vote = models.PositiveIntegerField(default = 0, blank = True,)
    opposing_vote = models.PositiveIntegerField(default = 0, blank = True,)
    vote_percent_share = models.PositiveSmallIntegerField(default=70,blank = True,)
    judge_percent_share = models.PositiveSmallIntegerField(default=30,blank = True,)
    class Meta:
        verbose_name_plural = 'Scores'

from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Extended Model used to add more details to User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    #Needed for allauth signup
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Practicing Lawyer, \
                                            Programmer, Business Man, Political Activist")
    date_of_birth = models.DateField(blank=True, null=True, help_text="yyyy/mm/dd")
    bio = models.TextField(blank=True, null=True)
    mobile_no = models.CharField(max_length=11, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True,
                                        help_text="e.g Lagos, New York")
    country = CountryField(blank_label='(select country)', default = "NG")
    participation_type = models.ManyToManyField('Participation', blank=True, related_name='participation_type')
    notify = models.BooleanField(default = True, help_text="Notify me of upcoming debates.")
    image = VersatileImageField(
        'Image', blank=True, null=True,
        upload_to='images/profile/',
        width_field='width',
        height_field='height'
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    optional_image = VersatileImageField(
        'Optional Image',
        upload_to='images/profile/optional/',
        blank=True,
        placeholder_image=OnDiscPlaceholderImage(
            path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'placeholder.png'
                )
            )
        )

    def get_absolute_url(self):
        return reverse('profile', args=[self.user.username,])

    def __str__(self):
        """
        String for representing the Custom User Model object (in Admin site etc.)
        """
        return self.user.get_full_name()


class PostDebater(models.Model):
    """
    Model used to by modetator to select debaters from a pool
    """
    DEBATE_POSITION_CHOICES = (
        ('opposing', 'Opposing'),
        ('supporting', 'Supporting'),
        ('judge', 'Judge'),
        ('moderator', 'Moderator')
        )
    name = models.ForeignKey(settings.AUTH_USER_MODEL)
    post = models.ForeignKey(PostDebate)
    debate_position = models.CharField(max_length=10, choices=DEBATE_POSITION_CHOICES)
    approval_status =  models.BooleanField('Approval Status', default=False)

class Participation(models.Model):
    """
    Model used to select what user intends to belong e.g. debate, follow, comment, moderate etc.
    """
    name = models.CharField(max_length=100, blank=True, null=True, )
    description = models.CharField(max_length=250,blank=True, null=True, )


    def __str__(self):
        return self.name

class Badge(models.Model):
    """
    Model used to reward debaters with badges for activities.
    """
    name = models.CharField(max_length=50,)
    description = models.CharField(max_length=250,null=True, blank=True)
    collected_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='collected_by')
    rank = models.PositiveSmallIntegerField()
    category = models.ForeignKey('Participation', blank=True,)
    wins = models.PositiveIntegerField(default=0, blank=True)
    loose = models.PositiveIntegerField(default=0, blank=True)
    suggested = models.PositiveIntegerField(default=0, blank=True)
    moderated = models.PositiveIntegerField(default=0, blank=True)
    judged = models.PositiveIntegerField(default=0, blank=True)

    def get_absolute_url(self):
        return reverse('debate:see_badge', args=[self.name,])
    def __str__(self):
        """
        String for representing the Badge Model object. Returns Badge Name and Category
        """
        return '{} ({})' .format(self.name, self.category)

class TrackedBadge(models.Model):
    """
    Model used to get user, time and date of badge award.
    """
    badge = models.ForeignKey(Badge)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    award_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('-award_date',)

    def __str__(self):
        """
        String for representing the TrackedBadge Model object. Returns User Name and Badge
        """
        return '{} ({})' .format(self.user.get_full_name(), self.badge)

class TrackedPost(models.Model):
    """
    Model used to track total unique visitors to a debate.
    """
    post = models.ForeignKey(PostDebate)
    ip = models.CharField(max_length=16) #only accounting for ipv4
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True) #if you want to track logged in or anonymous

class Suggest(models.Model):
    """
    Model used to suggest debate topics for review.
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default = User, blank=True, related_name='suggester')
    title = models.CharField(max_length=500)
    summary = models.TextField()
    tags = TaggableManager()
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return self.title

# Model for comment moderation
class PostCommentModerator(SpamModerator):
    email_notification = False
    auto_moderate_field = 'end'
    #moderate_after = 365 #in days

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
        return super(PostCommentModerator, self).moderate(comment,
                                                          content_object,
                                                          request)

moderator.register(PostDebate, PostCommentModerator)
