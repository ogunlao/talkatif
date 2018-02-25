from django.db import models
from django_countries.fields import CountryField #For Profile
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
import random
# Create your models here.

class Profile(models.Model):
    """
    Extended Model used to add more details to User model.
    """
    GENDER_CHOICES = (
        ('male', 'male'),
        ('female', 'female'),
        )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    #Needed for allauth signup
    other_name = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Practicing Lawyer, \
                                            Programmer, Business Man, Political Activist")
    date_of_birth = models.DateField(blank=True, null=True, help_text="yyyy/mm/dd")
    bio = models.TextField(blank=True, null=True, help_text="Tell us a little about yourself.")
    city = models.CharField(max_length=100, blank=True, null=True,
                                        help_text="e.g Lagos, New York")
    country = CountryField(blank_label='(select country)', null=True, blank=True)
    notify = models.BooleanField(default = True, help_text="Notify me of upcoming debates.")
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, blank=True, null=True)

    def profile_image_url(self):
        avatar_name = "avatar"+str(random.randint(1, 3))+".png" #random avatars if not found; avatar1, avatar2, avatar3
        return settings.MEDIA_URL+"avatars/default_avatar/"+avatar_name

    def get_absolute_url(self):
        return reverse('profile', args=[self.user.username,])

    def __str__(self):
        """
        String for representing the Custom User Model object (in Admin site etc.)
        """
        return self.user.username
