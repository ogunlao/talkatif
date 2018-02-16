from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import PostDebate, Profile, Votes, Notifyme, Stat,\
                Scores, Badge, Participation, TrackedPost, TrackedBadge, PostDebater
#import discourse
from discourse.models import Post
from django.contrib.auth.models import User
from .forms import PostDebateForm, UserForm, ProfileForm, ScoresForm, ModeratorForm
from discourse.forms import PostForm
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from meta.views import Meta #to include metatags in view for display, check django-meta
from taggit.models import Tag
import random
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

#Default meta details for post
meta = Meta(
    title="Welcome to Talkatif. Home to debates, opinions, arguments and talks. A talking family.",
    description="talkatif.com creates an environment for interesting talks, debates, arguments and opinions.",
    url="/",
    extra_props = {
        #'viewport': 'width=device-width, initial-scale=1.0, minimum-scale=1.0'
    }
)

def index(request):
    if request.user.is_authenticated():
        return redirect('all_list', permanent=True )
    else:
        return render(request, 'index.html', {'meta':meta})

from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser)
@login_required
def dashboard(request):
    total_users= User.objects.all().count()
    return render(request, 'dashboard.html', {'total_users':total_users, 'meta':meta,})

def all_list(request):
    post_list = PostDebate.published.all()
    object_list = Post.published.all()
    merged_list = []
    merged_list.extend(post_list)
    merged_list.extend(object_list)

    #sorting the list by created date
    def getKey(item):
        return item.created
    merged_list = sorted(merged_list, key=getKey, reverse=True)

    #Get last 5 badge winners
    last_5_badges = TrackedBadge.objects.all()[:5]


    paginator = Paginator(merged_list, 50) # Show 50 posts per page
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    except EmptyPage:
        page = paginator.num_pages

    merged_list = paginator.page(page)


    context = {'merged_list': merged_list, 'last_5_badges':last_5_badges, 'meta':meta,}
    template = 'all_list.html'

    return render(request, template , context)

def debate_list(request, tag_slug = None, category = None):
    object_list = PostDebate.published.all()
    tag = None
    section = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    if category:
        object_list = object_list.filter(debate_category=category)

    paginator = Paginator(object_list, 50) # Show 50 posts per page

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    except EmptyPage:
        page = paginator.num_pages

    object_list = paginator.page(page)
    last_5_badges = TrackedBadge.objects.all()[:5]

    template = 'debate/post/debate_list.html'
    context = {'object_list': object_list, 'tag':tag,  'page': page, 'last_5_badges':last_5_badges, 'meta':meta }
    return render(request, template , context)

#A function to get the ip host of logged in user
#Used to track activities and get total user views
from ipware import get_client_ip

def client_ip(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        return "127.0.0.1"
    else:
        return client_ip

# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip

def debate_detail(request, post_id, category=None,  post_slug=None):
    post = get_object_or_404(PostDebate, pk=post_id)
    similar_posts = post.tags.similar_objects()[:5] #Get five other similar posts

    user_id = request.user.pk

    #Checks and increment count of visits
    #you could check for logged in users as well
    ip_add = client_ip(request) #gets user ip address
    if request.user.is_authenticated(): #To save user data for page views
        request_user = request.user
    else: request_user = None
    #Create the user in the database if not found, added to total views number
    tracked_post, created = TrackedPost.objects.get_or_create(post=post, ip=ip_add, user=request_user) #note, not actual api
    if created:
        tracked_post.post.count += 1 #increases count on post
        tracked_post.post.save()

    #Get what user voted for
    vote_message = ""
    if Votes.objects.filter(post = post).filter(voter = user_id).exists():
        status = Votes.objects.filter(post = post).get(voter = user_id) #Checks if user has voted before
        if status.support == True:
            vote_message = "You have voted for the supporting team"
        elif status.oppose == True:
            vote_message = "You have voted for the opposing team"

    #Checks if user has click notify button earlier
    notify_status = Notifyme.objects.filter(post = post).filter(user_notify = user_id).exists()

    liked = False
    #Checks if user have liked before
    for person in post.likes.all():
        if person == request_user:
            liked = True
            break

    #Function for adding stats to debates. Need to be updated
    if not post.stats_updated and post.end and post.end < timezone.now(): #debate has ended but stats not updated
        stat_updater = Stat()
        post_moderator = post.moderator.all()
        if post_moderator: #Updates stats for all moderators.
            for people in post_moderator:
                stat_updater = Stat()
                stat_updater.post = post
                stat_updater.person = people
                stat_updater.moderated = True
                stat_updater.save()

        post_supporting_debaters = post.supporting_debaters.all()
        if post_supporting_debaters: #Updates stats for suppoting group
            for people in post_supporting_debaters:
                stat_updater = Stat()
                stat_updater.post = post
                stat_updater.person = people
                stat_updater.supported = True
                stat_updater.save()
        post_opposing_debaters = post.opposing_debaters.all()
        if post_opposing_debaters: #Updates stats for opposing group
            for people in post_opposing_debaters:
                stat_updater = Stat()
                stat_updater.post = post
                stat_updater.person = people
                stat_updater.opposed = True
                stat_updater.save()
        post_judges = post.judges.all()
        if post.judges.all(): #Updates stats for opposing group
            for people in post_judges:
                stat_updater = Stat()
                stat_updater.post = post
                stat_updater.person = people
                stat_updater.judged = True
                stat_updater.save()
        post.stats_updated = True
        post.save()

    total_support_vote = Votes.objects.filter(post = post).filter(support = True).count()
    total_oppose_vote = Votes.objects.filter(post = post).filter(oppose = True).count()
    like_count = post.total_likes #counts total likes on post

    #Time comparism
    debate_in_progress = debate_has_ended = voting_has_started = False
    if post.end and post.begin:
        if timezone.now() > post.begin and timezone.now() < post.end:
            debate_in_progress = True
        if timezone.now() > post.end:
            debate_has_ended = True

    elif post.begin:
        if timezone.now() > post.begin:
            debate_in_progress = True

    if post.vote_starts:
        if timezone.now() > post.vote_starts and debate_in_progress and request.user.is_authenticated(): #enable voting for users
            voting_has_started = True

    #Gets meta details for post
    meta = Meta(
        title=post.title,
        description=post.summary,
        keywords=post.tags.all(),
        url=post.get_absolute_url(),
        extra_props = {
            #'viewport': 'width=device-width, initial-scale=1.0, minimum-scale=1.0'
        }
    )

    #use ajax
    deb_stat = Stat.objects.all()
    all_badges = Badge.objects.all()

    #user_in_debate = post.supporting_debaters.all().filter(supporting_debaters__pk=request.user.id)
    user_in_supporting_team = post.supporting_debaters.all().filter(id=request.user.id)
    user_in_opposing_team = post.opposing_debaters.all().filter(id=request.user.id)
    user_is_moderator = post.moderator.all().filter(id=request.user.id)
    user_is_judge = post.judges.all().filter(id=request.user.id)

    #Check to see if comment form can be enabled
    if (post.debate_category == "open" and request.user.is_authenticated()) or user_is_moderator:
        open_comment = True
    elif (user_in_supporting_team or user_in_opposing_team or user_is_judge) and debate_in_progress:
        open_comment = True
    elif debate_has_ended and request.user.is_authenticated() and post.allow_follower_comment:
        open_comment = True
    else:
        open_comment = False

    context = {'post': post, 'meta' : meta, 'similar_posts':similar_posts, 'like_count' : like_count, 'liked' : liked, 'vote_message' : vote_message,
            'total_support_vote' : total_support_vote, 'total_oppose_vote' : total_oppose_vote, 'notify_status' : notify_status,
            'debate_in_progress': debate_in_progress, 'debate_has_ended':debate_has_ended, 'deb_stat':deb_stat, \
            'user_in_supporting_team':user_in_supporting_team, \
            'user_in_opposing_team':user_in_opposing_team, 'user_is_moderator':user_is_moderator, \
            'user_is_judge':user_is_judge, 'open_comment':open_comment, 'voting_has_started':voting_has_started }

    return render(request, 'debate/post/debate_detail.html', context)

@login_required
def join_participants(request, post_id, position):
    post = get_object_or_404(PostDebate, id=post_id)

    new_post = PostDebater()
    #Max of 5 debaters on each team
    new_post.post = post
    new_post.name = request.user
    status = PostDebater.objects.filter(post=post).filter(name=request.user) #check if previously added
    if not status:
        if position == "supporting":
                new_post.debate_position = "supporting"
                messages.success(request, 'You have been added to the supporting team queue. You would be notified by mail 1 hr before or earlier if selected')
                new_post.save()
        elif position == "opposing":
            new_post.debate_position = "opposing"
            messages.success(request, 'You have been added to the opposing team queue. You would be notified by mail 1 hr before or earlier if  selected')
            new_post.save()
    else:
        messages.info(request, 'You have been previously added to the queue. Do not show interest again!')
    return redirect('debate:debate_detail', category = post.debate_category, post_id=post.pk, \
            post_slug = post.slug, )


from PIL import Image as Img

@login_required
def new_post(request, post_id = None):
    sent = False
    post = PostDebate()
    if post_id: #if instance of post is to be edited
        post = get_object_or_404(PostDebate, pk = post_id)

    if request.method == 'POST':
        # Form was submitted
        form = PostDebateForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.debate_category == "open":
                post.begin = timezone.now()
            try:
                post.save()
                form.save_m2m()
            except IntegrityError as e:
                if 'unique constraint' in e.args[0]:
                #if 'unique constraint' in e.message: # or e.args[0] from Django 1.10
                    message_info = "Post has previously been saved."
                    messages.info(request, message_info )
                return redirect('all_list')
            sent = True
            post = get_object_or_404(PostDebate, title = post.title )
            post.moderator.add(request.user)
            post.save()
            message_info = "Debate uploaded Successfully! You have been made a debate moderator. Choose time to start and end debate"
            messages.info(request, message_info )
            if post.debate_category == "closed":
                message_info = "Debaters can now add theselves to debate."
                messages.info(request, message_info )
            return redirect('debate:debate_detail', category = post.debate_category, post_id=post.id, \
                    post_slug = post.slug )
    else:
        form = PostDebateForm(instance=post)
        context = {'form': form, 'sent': sent, 'post_id':post_id, 'meta':meta}
        return render(request, 'debate/form/new_debate.html', context)

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    post, created = Profile.objects.get_or_create(user=profile_user)

    if created:
        message_info = 'Welcome to your profile! A username '+username+' was auto generated for you. Edit your profile.'
        messages.info(request, message_info)

    #Get various posts accourding to categories
    debate_involved = Stat.objects.filter(person = profile_user)
    moderated = debate_involved.filter(moderated = True)
    judged = debate_involved.filter(judged = True)
    supported = debate_involved.filter(supported = True)
    opposed = debate_involved.filter(opposed = True)
    won = debate_involved.filter(won = True)
    lost = debate_involved.filter(lost = True)
    drew = debate_involved.filter(drew = True)

    all_badge = Badge.objects.all()

    badges = all_badge.filter(collected_by__in = [profile_user.pk])
    suggester = PostDebate.objects.filter(author = profile_user).count()

    won_count = moderated_count = judged_count = 0
    profile_user_name = profile_user.get_full_name()
    if badges:
        track_badge = TrackedBadge() #instance to track badges esp latest badges
        #Time to assign new badges for profile if found worthy
        #Get ids of categories
        id_debater = Participation.objects.get(name = "debater")
        id_moderator = Participation.objects.get(name = "moderator")
        id_suggester = Participation.objects.get(name = "content creator")
        id_judge = Participation.objects.get(name = "judge")

        debater_badge = all_badge.filter(category = id_debater.pk)
        moderator_badge = all_badge.filter(category = id_moderator.pk)
        judge_badge = all_badge.filter(category = id_judge.pk)
        suggester_badge = all_badge.filter(category = id_suggester.pk)

        won_count = won.count()
        moderated_count = moderated.count()
        judged_count = judged.count()

        if won_count:
            for badge in debater_badge:
                if won_count >= badge.wins: #update debaters badges according to winnings
                    ignore = False
                    for person in badge.collected_by.all(): #check if user has already been assigned the badge
                        if profile_user == person:
                            ignore = True
                            break

                    if not ignore:
                        badge.collected_by.add(profile_user)
                        badge.save()
                        #Track saved badges for wins
                        track_badge = TrackedBadge()
                        track_badge.badge = badge
                        track_badge.user = profile_user
                        track_badge.save()

                        message_info= 'Hurray!! New Debaters badge >'+badge.name+ '< given to '+profile_user_name+' for winning '+ str(won_count)+' debate(s)'
                        messages.info(request, message_info )
        if moderated_count:
            for badge in moderator_badge:
                if moderated_count >= badge.moderated:
                    ignore = False
                    for person in badge.collected_by.all():
                        if profile_user == person:
                            ignore = True
                            break
                    if not ignore:
                        badge.collected_by.add(profile_user)
                        badge.save()

                        #Track saved badges for moderation
                        track_badge = TrackedBadge()
                        track_badge.badge = badge
                        track_badge.user = profile_user
                        track_badge.save()
                        message_info = 'Hurray!! New Moderators badge >'+badge.name+ '< given to '+profile_user_name+' for moderating '+str(moderated_count)+' debate(s)'
                        messages.info(request, message_info)

        if judged_count:
            for badge in judge_badge:
                if judged_count >= badge.judged:
                    ignore = False
                    for person in badge.collected_by.all():
                        if profile_user == person:
                            ignore = True
                            break
                    if not ignore:
                        badge.collected_by.add(profile_user)
                        badge.save()
                        #Track saved badges for judges
                        track_badge = TrackedBadge()
                        track_badge.badge = badge
                        track_badge.user = profile_user
                        track_badge.save()

                        message_info = 'Hurray!! New Judges badge >'+badge.name.title()+ '< given to '+profile_user_name+' for judging '+str(judged.count())+' debates'
                        messages.info(request, message_info)

        if suggester: #suggester is an author of a debate post. He suggested the topic
            for badge in suggester_badge:
                if suggester >= badge.suggested:
                    ignore = False
                    print("suggester is greater")
                    for person in badge.collected_by.all():
                        if profile_user == person:
                            ignore = True
                            break

                    if not ignore:
                        badge.collected_by.add(profile_user)
                        badge.save()
                        #Track saved badges
                        track_badge = TrackedBadge()
                        track_badge.badge = badge
                        track_badge.user = profile_user
                        track_badge.save()

                        messages.info(request, 'Hurray!! New Community badge >'+ badge.name.title()+ '< given to '+profile_user_name+' for creating ' +str(suggester)+' debate post')

    context = {'post': post, 'profile_user': profile_user, 'moderated':moderated,'judged':judged, 'supported':supported, 'opposed':opposed, \
                'won':won, 'lost': lost, 'drew':drew, 'debate_involved': debate_involved, 'badges':badges,
                'won_count':won_count, 'moderated_count':moderated_count, 'judged_count':judged_count,
                'profile_user_name':profile_user_name, 'created':created, 'meta':meta}
    return render(request, 'account/profile.html', context)

@login_required
def deactivate_profile(request):
    admin_email = settings.ADMIN_EMAIL
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        messages.success(request, 'Profile successfully disabled.')

        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        import datetime
        now = datetime.datetime.now()
        dvalues = {'full_name':user.get_full_name(), 'username':user.username, 'deactivation_date':now, 'admin_email':admin_email}
        body = render_to_string('deactivation_mail.txt', dvalues)

        send_mail(
        'Deactivation of talkatif.com account',
        body,
        admin_email,
        [user.email],
        fail_silently=True,
            )
        return redirect('index')

    else:
        return render(request, 'account/deactivate_profile.html', {'admin_email':admin_email, 'meta':meta})

@login_required
def mod_debate(request, post_id):
    related_post = get_object_or_404(PostDebate, id = post_id)
    debaters_supporting = PostDebater.objects.filter(post=related_post).filter(debate_position="supporting")
    debaters_opposing = PostDebater.objects.filter(post=related_post).filter(debate_position="opposing")

    if request.method == 'POST':
        mod_form = ModeratorForm(request.POST, instance=related_post)

        #Get checkbox status to allow outside comments
        allow_follower_comment = request.POST.get("allow_follower_comment", None)
        if not allow_follower_comment:
            related_post.allow_follower_comment = False
            related_post.save()
            messages.success(request, 'Comments disabled from followers')

        if mod_form.is_valid():
            mod_form.save()
            messages.success(request, 'Date Changes applied.')
            return redirect('debate:debate_detail', category =related_post.debate_category, \
                    post_id = related_post.pk, post_slug = related_post.slug)
        else:
            messages.error(request, _('Date update failed. Dates are invalid.'))
    else:
        mod_form = ModeratorForm(instance=related_post)
        postdebate_form = PostDebateForm(instance=related_post)
    context = {'mod_form': mod_form, 'related_post':related_post, 'debaters_supporting':debaters_supporting,\
    'debaters_opposing':debaters_opposing, 'postdebate_form':postdebate_form, 'meta':meta }
    return render(request, 'debate/form/mod_panel.html', context)



@login_required
def score_debate(request, post_id):
    scored = False #Has judges given their verdict?
    calculated = False #Has total scores been calculated
    related_post = get_object_or_404(PostDebate, id = post_id)
    status = Scores.objects.filter(post = related_post).exists() #Has debate previously been scored?
    judge_available = related_post.judges.all().count() #Are judges included in debate? 0 indiates non
    vote_ended = False
    if timezone.now() > related_post.end:
        vote_ended = True
    if not status and not vote_ended: #Allow judge scores only if debate has not ended
        if request.method == 'POST':
            score_form = ScoresForm(request.POST)
            if score_form.is_valid():
                post = score_form.save(commit=False)
                post.post = related_post
                post.uploaded_by = request.user
                post.save()
                scored = True
                messages.success(request, 'Debate score updated successfully')
                return render(request, 'debate/form/score.html', {'post': post, 'scored':scored})
            else:
                print (score_form.errors)
        else:
            #Display form when scores is yet to be submitted
            score_form = ScoresForm()
            context = {'score_form': score_form, 'scored': scored, 'related_post' : related_post }
            return render(request, 'debate/form/score.html', context )

    else:
        post, created = Scores.objects.get_or_create(post=related_post)
        if not related_post.winner_updated:
            #Get total votes for both side  and keep updating as users view it
            total_support_vote = Votes.objects.filter(post = related_post).filter(support = True).count()
            total_oppose_vote = Votes.objects.filter(post = related_post).filter(oppose = True).count()

            post.supporting_vote = total_support_vote
            post.opposing_vote = total_oppose_vote

            scored = True #Scores has now been updated

            #check if debate has ended before calculating scores
            judge_support_percent = judge_oppose_percent = total_votes = vote_support_percent = vote_oppose_percent = 0
            supporting_team_percent_score = opposing_team_percent_score = 0 #initialization
            #calculating Winner

            total_votes = post.supporting_vote + post.opposing_vote
            if related_post.debate_category == "closed" and judge_available:
                #Assuming debate is closed and judges are to give verdict
                judge_support_percent = (post.supporting_score / post.highest_score) * post.judge_percent_share
                judge_oppose_percent = (post.opposing_score / post.highest_score) * post.judge_percent_share

                vote_support_percent = (post.supporting_vote / total_votes) * post.vote_percent_share
                vote_oppose_percent = (post.opposing_vote / total_votes) * post.vote_percent_share
            else:
                #Use votes only, 100 percent used
                vote_support_percent = (post.supporting_vote / total_votes) * 100
                vote_oppose_percent = (post.opposing_vote / total_votes) * 100

            supporting_team_percent_score = vote_support_percent + judge_support_percent
            opposing_team_percent_score = vote_oppose_percent + judge_oppose_percent

            post.st_verdict = supporting_team_percent_score
            post.ot_verdict = opposing_team_percent_score

            #Update Statistics for winners and loosers
            stats_update_supporting = Stat.objects.filter(post = related_post).filter(supported = True)
            stats_update_opposing = Stat.objects.filter(post = related_post).filter(opposed = True)
            if supporting_team_percent_score > opposing_team_percent_score:
                for update in stats_update_supporting:
                    update.won = True
                    update.save()
                for update in stats_update_opposing:
                    update.lost = True
                    update.save()
                related_post.winner = "supporting" #Update post as supporting team won
            elif supporting_team_percent_score < opposing_team_percent_score:
                for update in stats_update_opposing:
                    update.won = True
                    update.save()
                for update in stats_update_supporting:
                    update.lost = True
                    update.save()
                related_post.winner = "opposing" #Update post as opposing team won
            elif supporting_team_percent_score == opposing_team_percent_score:
                for update in stats_update_opposing:
                    update.drew = True
                    update.save()
                for update in stats_update_supporting:
                    update.drew = True
                    update.save()
                related_post.winner = "draw" #Update post as it ended in a tie
            related_post.winner_updated = True
            related_post.save()
            post.save()

        context = {'scored': scored, 'post': post, 'related_post':related_post,
        'meta':meta }

        return render(request, 'debate/form/score.html', context )

from django.db import transaction
from django.utils.translation import gettext as _

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile', username =request.user.username)

        else:
            messages.error(request, _('Please correct the error in red text.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'account/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'meta':meta,
    })

def see_badge(request):

    post = Badge.objects.all()

    return render(request, 'debate/post/badge.html', {
        'post':post, 'meta':meta,
    })


def rules_guidelines(request):
    return render(request, 'debate/post/rules_guidelines.html', {'meta':meta })

def faq(request):
    return render(request, 'faq.html', {'meta':meta })

from django.http import HttpResponse
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.views.decorators.http import require_POST

@login_required
@require_POST
def like(request):
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        post = get_object_or_404(PostDebate, slug=slug)
        liked = False
        if post.likes.filter(id=user.id).exists():
            # user has already liked this debate post
            # remove like/user
            post.likes.remove(user)
            message = 'You disliked this'
        else:
            # add a new like for the post
            post.likes.add(user)
            liked = True
            message = 'You liked this'

    ctx = {'likes_count': post.total_likes, 'liked':liked, 'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')

from django.http import HttpResponseRedirect

def go_to(request, category, post_slug):
    goto_page_no = request.GET.get('goto')
    try:
        goto_page_no = int(goto_page_no)
    except ValueError:
        goto_page_no = 1
    url = "reverse('debate:go_to', kwargs={'category':category, 'post_id':post_id, 'post_slug':post_slug, 'goto_page_no':goto_page_no})"
    return HttpResponseRedirect('url')

from django.http import HttpResponse
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.views.decorators.http import require_POST

@login_required
@require_POST
def vote(request):
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        debate_stand = request.POST.get('debate_stand', None)
        post = get_object_or_404(PostDebate, slug=slug)
        votes = Votes()
        status = Votes.objects.filter(voter = user.id).filter(post = post) #Checks if user has voted before
        if Votes.objects.filter(voter = user.id).filter(post = post).exists(): #Checks if user has voted before
            message = 'You have voted earlier'
        elif debate_stand == 'support':
            debate_stand = "supporting" #change necessary for html output
            votes.voter = user #user who voted
            votes.post = post #post voted on
            votes.support = True
            votes.save()
            message = 'You have voted for the supporting team'
        elif debate_stand == 'oppose':
            debate_stand = "supporting" #change necessary for html output
            votes.voter = user #user who voted
            votes.post = post #post voted on
            votes.oppose = True
            votes.save()
            message = 'You have voted for the opposing team'

    ctx = {'debate_stand': debate_stand, 'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')

@login_required
@require_POST
def notify(request):
    if request.method == 'POST':
        slug = request.POST.get('slug', None)
        post = get_object_or_404(PostDebate, slug=slug)
        notify_status = Notifyme.objects.filter(post = post).filter(user_notify = request.user).exists()
        if notify_status: #user has not previously applied to be notified
            message = 'You have previously set notification for this debate. You would be notified via email 15 mins before debate starts'
        else:
            notify = Notifyme()
            notify.post = post
            notify.user_notify = request.user
            notify.save()
            message = 'You would be notified via email 15 mins before debate starts'

    ctx = {'notiify_status': notify_status, 'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')

@login_required
@require_POST
def approve(request):
    if request.method == 'POST':
        user_id = int(request.POST.get('user_id', None))
        post_id = int(request.POST.get('post_id', None))
        position = request.POST.get('position', None)
        approve = request.POST.get('approve', None) #used to detect approval and disapproval

        post = get_object_or_404(PostDebate, id=post_id)
        user = get_object_or_404(User, id=user_id)
        debater = get_object_or_404(PostDebater, post=post, name=user)

        approved = False #used to detect state of user addition to debate team
        if position == "supporting":
            if approve == "yes":
                post.supporting_debaters.add(user)
                debater.approval_status = True
                approved = True
            elif approve == "no":
                post.supporting_debaters.remove(user) #disapprove user addition to debate team
                debater.approval_status = False
            debater.save()
        elif position == "opposing":
            if approve == "yes":
                post.opposing_debaters.add(user)
                debater.approval_status = True
                approved = True
            elif approve == "no":
                post.opposing_debaters.remove(user)
                debater.approval_status = False
            debater.save()

    ctx = {'approved': approved, 'username': user.username, }
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')
