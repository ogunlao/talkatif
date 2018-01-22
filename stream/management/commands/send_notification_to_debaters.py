from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
#from django.core.mail import send_mass_mail
from stream.models import PostDebate
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
    Function to get all the posts starting 1 hours or later that have had their participants sent notification
    """
    schedule_post = PostDebate.objects.filter(begin__lte = schedule_time).filter(debate_notification = False)
    return schedule_post

def notify_all(schedule_post):
    """
    Function to notify debaters, judges and moderators when debate starts
    """
    for notification_post in schedule_post:
        if notification_post:
            subject = "Notification from Puto.ng"
            message_list = message_detail = []
            if notification_post.moderator.all(): #checks if there are modertors
                for person in notification_post.moderator.all():
                    html_content = render_to_string('notification_template.html', {'name':person.get_full_name(),\
                            'debate_job' : 'moderating', 'debate_title':notification_post.title,\
                            'debate_summary':notification_post.summary, 'debate_team':notification_post.moderator.all()})
                    message = strip_tags(html_content) #strips the html of tags to get the raw text.
                    recipients_email = person.email
                    message_detail = EmailMultiAlternatives(subject, message, from_email, [recipients_email])
                    message_detail.attach_alternative(html_content,"text/html")
                    message_list.append(message_detail)

            if notification_post.supporting_debaters.all():
                for person in notification_post.supporting_debaters.all():
                    html_content = render_to_string('notification_template.html', {'name':person.get_full_name(),\
                            'debate_job' : 'supporting', 'debate_title':notification_post.title,\
                            'debate_time':notification_post.begin, \
                            'debate_summary':notification_post.summary, 'debate_team':notification_post.supporting_debaters.all()})
                    message = strip_tags(html_content) #strips the html of tags to get the raw text.
                    recipients_email = person.email
                    message_detail = EmailMultiAlternatives(subject, message, from_email, [recipients_email])
                    message_detail.attach_alternative(html_content,"text/html")
                    message_list.append(message_detail)

            if notification_post.opposing_debaters.all():
                for person in notification_post.opposing_debaters.all():
                    html_content = render_to_string('notification_template.html', {'name':person.get_full_name(),\
                            'debate_job' : 'opposing', 'debate_title':notification_post.title,\
                            'debate_summary':notification_post.summary, 'debate_team':notification_post.opposing_debaters.all()})
                    message = strip_tags(html_content) #strips the html of tags to get the raw text.
                    recipients_email = person.email
                    message_detail = EmailMultiAlternatives(subject, message, from_email, [recipients_email])
                    message_detail.attach_alternative(html_content,"text/html")
                    message_list.append(message_detail)

            if notification_post.judges.all():
                for person in notification_post.judges.all():
                    html_content = render_to_string('notification_template.html', {'name':person.get_full_name(),\
                            'debate_job' : 'judges', 'debate_title':notification_post.title,\
                            'debate_summary':notification_post.summary, 'debate_team':notification_post.judges.all()})
                    message = strip_tags(html_content) #strips the html of tags to get the raw text.
                    recipients_email = person.email
                    message_detail = EmailMultiAlternatives(subject, message, from_email, [recipients_email])
                    message_detail.attach_alternative(html_content,"text/html")
                    message_list.append(message_detail)

            total_mail_sent = connection.send_messages(message_list)
            connection.close()
            #total_mail_sent = send_mass_mail(tuple(message_list), fail_silently=False)
            if total_mail_sent:
                notification_post.debate_notification = True
                notification_post.save()
    return True

class Command(BaseCommand):
    help = 'Starts sending notifications to debaters, moderators and judges'
    def handle(self, *args, **options):
        self.stdout.write("Notification job started for participants " + str(timezone.now()), ending='')
        schedule_time = timezone.now() + datetime.timedelta(hours=23)
        schedule_post = notify_post(schedule_time)
        if schedule_post or True:
            send_mail = notify_all(schedule_post)
        if send_mail:
            self.stdout.write(" Mails sent")
