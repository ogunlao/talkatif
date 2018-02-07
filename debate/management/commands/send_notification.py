from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
#from django.core.mail import send_mass_mail
from debate.models import PostDebate, Notifyme
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags

connection = get_connection()
connection.open()
message_list = list()


from_email = settings.SERVER_EMAIL

def notify_post(schedule_time):
    """
    Function to get all posts starting soon with users wanting to be notified.
    """
    schedule_post = PostDebate.objects.filter(begin__lte = schedule_time)
    return schedule_post

def notify_all(schedule_post):
    """
    Function to notify users when debate starts
    """
    for posts in schedule_post:
        notification_list = Notifyme.objects.filter(post = posts).filter(notified = False)
        if notification_list:
            subject = "Debate Notification from talkatif.com"
            message_list = []
            for lists in notification_list:
                recipients_email = lists.user_notify.email
                ctx = {'name':lists.user_notify.get_full_name(),\
                         'debate_title':posts.title, \
                         'debate_time':posts.begin,'debate_summary':posts.summary,\
                         'debate_url':"https://talkatif.com"+str(posts.get_absolute_url()), 'admin_email':settings.SERVER_EMAIL}
                html_content = render_to_string('debate_subscribers_template.html', ctx)
                message = strip_tags(html_content) #strips the html of tags to get the raw text.
                recipients_email = lists.user_notify.email
                message_detail = EmailMultiAlternatives(subject, message, from_email, [recipients_email])
                message_detail.attach_alternative(html_content,"text/html")
                message_list.append(message_detail)

            total_mail_sent = connection.send_messages(message_list)
            connection.close()

            for recipient in notification_list:
                if total_mail_sent:
                    recipient.notified = True
                    recipient.save()
    return "Sent"

class Command(BaseCommand):
    help = 'Starts sending notifications to user'
    def handle(self, *args, **options):
        self.stdout.write("Notification job started " + str(timezone.now()), ending='')
        schedule_time = timezone.now() + datetime.timedelta(minutes=15)
        schedule_post = notify_post(schedule_time)
        if schedule_post or True:
            send_mail = notify_all(schedule_post)
        if send_mail:
            self.stdout.write(" Mails sent")
