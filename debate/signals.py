from allauth.account.signals import email_confirmed, user_signed_up
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User

#Used to get facebook user profile
from allauth.socialaccount.models import SocialAccount

from discourse.models import Post
from debate.models import Profile, PostDebate

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags

@receiver(user_signed_up)
def set_initial_user_names(request, user, sociallogin=None, **kwargs):
    """
    sociallogin.account.provider  # e.g. 'twitter'
    sociallogin.account.get_avatar_url()
    sociallogin.account.get_profile_url()
    sociallogin.account.extra_data['screen_name']
    """

    profile = Profile()
    if sociallogin:
        if sociallogin.account.provider == 'facebook':
            profile.gender_type = sociallogin.account.extra_data['gender']
            #verified = sociallogin.account.extra_data['verified']

    #I want to get country and city of user from ip address.
    from ipware import get_client_ip
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        pass # Unable to get the client's IP address
    else:
    # We got the client's IP address
        if is_routable: # The client's IP address is publicly routable on the Internet
            import requests
            r = requests.get('http://usercountry.com/v1.0/json/'+str(client_ip))
            result = r.json()
            if result['status'] == "success":
                profile.country = result['country']['alpha-2']
                profile.city = result['region']['city']
            else: #result returns failure
                pass
        else:
            pass # The client's IP address is private

    profile.user = user
    profile.save()


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    """
    Signal to send welcome message to user on first login
    """
    postdebate = PostDebate.objects.filter()[:5]
    post = Post.objects.filter()[:5]
    user = User.objects.get(email=email_address.email)

    # user.is_active = True
    # user.save()
    ctx = {'postdebate':postdebate, 'post':post, 'user':user, 'admin_email':settings.ADMIN_EMAIL}
    from_email = settings.NOTIFICATION_EMAIL
    recipients_email = user.email
    subject = "Welcome to the Talkatif Community."
    html_content = render_to_string('welcome_mail.html', ctx)
    message = strip_tags(html_content) #strips the html of tags to get the raw text.
    msg = EmailMultiAlternatives(subject, message, from_email, [recipients_email])
    msg.attach_alternative(html_content,"text/html")
    msg.send()


import urllib.request

from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.dispatch import receiver

from avatar.models import Avatar
from allauth.account.signals import user_signed_up

def name_from_url(url):
    """
    >>> name_from_url('http://google.com/dir/file.ext')
    u'file.ext'
    >>> name_from_url('http://google.com/dir/')
    u'dir'
    >>> name_from_url('http://google.com/dir')
    u'dir'
    >>> name_from_url('http://google.com/dir/..')
    u'dir'
    >>> name_from_url('http://google.com/dir/../')
    u'dir'
    >>> name_from_url('http://google.com')
    u'google.com'
    >>> name_from_url('http://google.com/dir/subdir/file..ext')
    u'file.ext'
    """
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse
    p = urlparse(url)
    for base in (p.path.split('/')[-1],
                 p.path,
                 p.netloc):
        name = ".".join(filter(lambda s: s,
                               map(slugify, base.split("."))))
        if name:
            return name


def copy_avatar(request, user, account):
    url = account.get_avatar_url()
    if url:
        ava = Avatar(user=user)
        ava.primary = Avatar.objects.filter(user=user).count() == 0
        try:
            content = urllib.request.urlopen(url).read()
            name = name_from_url(url)
            ava.avatar.save(name, ContentFile(content))
        except IOError:
            # Let's nog make a big deal out of this...
            pass


@receiver(user_signed_up)
def on_user_signed_up(sender, request, *args, **kwargs):
    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        copy_avatar(request,
                    sociallogin.account.user,
                    sociallogin.account)
