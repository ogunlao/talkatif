from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, reverse
from django.contrib.auth.decorators import login_required
from .models import PostDebate, Profile, Votes, Notifyme, Stat,\
                Scores, Badge, Participation, TrackedPost, TrackedBadge, Attachment, PostDebater
import discourse
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
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    if request.user.is_authenticated():
        return redirect('all_list', permanent=True )
    else:
        return render(request, 'index.html', {})

from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser)
@login_required
def dashboard(request):
    total_users= User.objects.all().count()
    return render(request, 'dashboard.html', {'total_users':total_users})

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

    form = PostForm() #for post for on main page
    #Get last 5 badge winners
    last_5_badges = TrackedBadge.objects.all()[:5]


    paginator = Paginator(merged_list, 4) # Show 4 posts per page
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    except EmptyPage:
        page = paginator.num_pages

    merged_list = paginator.page(page)


    context = {'merged_list': merged_list, 'form':form, 'last_5_badges':last_5_badges,}
    template = 'all_list.html'

    return render(request, template , context)

def debate_list(request, tag_slug = None, category = None):
    object_list = PostDebate.published.all()

    form = PostDebateForm()
    tag = None
    section = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    if category:
        object_list = object_list.filter(debate_category=category)

    paginator = Paginator(object_list, 20) # Show 20 posts per page

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    except EmptyPage:
        page = paginator.num_pages

    object_list = paginator.page(page)
    last_5_badges = TrackedBadge.objects.all()[:5]

    template = 'debate/post/debate_list.html'
    context = {'object_list': object_list, 'tag':tag,  'page': page, 'last_5_badges':last_5_badges, \
            'form':form,}
    return render(request, template , context)

#A function to get the ip host of loggen in user
#Used to track activities and get total user views
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def debate_detail(request, post_id, category=None,  post_slug=None):
    post = get_object_or_404(PostDebate, pk=post_id)
    user_id = request.user.pk

    attachments = Attachment.objects.filter(post = post)

    #Checks and increment count of visits
    #you could check for logged in users as well
    ip_add = get_client_ip(request) #gets user ip address
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
    debate_in_progress = debate_has_ended = False
    if post.end:
        if timezone.now() > post.begin and timezone.now() < post.end:
            debate_in_progress = True
        if timezone.now() > post.end:
            debate_has_ended = True

    elif post.begin:
        if timezone.now() > post.begin:
            debate_in_progress = True

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

    context = {'post': post, 'meta' : meta, 'like_count' : like_count, 'liked' : liked, 'vote_message' : vote_message,
            'total_support_vote' : total_support_vote, 'total_oppose_vote' : total_oppose_vote, 'notify_status' : notify_status,
            'debate_in_progress': debate_in_progress, 'debate_has_ended':debate_has_ended, 'deb_stat':deb_stat, \
            'attachments':attachments, 'user_in_supporting_team':user_in_supporting_team, \
            'user_in_opposing_team':user_in_opposing_team, 'user_is_moderator':user_is_moderator, \
            'user_is_judge':user_is_judge }
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
            post_slug = post.slug )


from PIL import Image as Img

@login_required
def new_post(request, post_id = None):
    sent = False
    post = PostDebate()
    num_image_attached = 0 #checks if some images have been previously added
    if post_id: #if instance of post is to be edited
        post = get_object_or_404(PostDebate, pk = post_id)
        num_image_attached = Attachment.objects.filter(post = post).count()

    if request.method == 'POST':
        # Form was submitted
        form = PostDebateForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # Form fields passed validation
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
            #Saves post attachments
            images_attached = form.cleaned_data['attachment']
            if images_attached:
                for each in images_attached:
                    Attachment.objects.create(file=each, post = post)

                for each in Attachment.objects.filter(post=post): #Compress image
                    print (settings.MEDIA_ROOT +"/"+ str(each))
                    img = Img.open(settings.MEDIA_ROOT +"/"+ str(each))
                    img.save(settings.MEDIA_ROOT +"/"+ str(each),quality=70,optimize=True)

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
        content = {'form': form, 'sent': sent, 'post_id':post_id, 'num_image_attached':num_image_attached}
        return render(request, 'debate/form/new_debate.html', content)

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    post, created = Profile.objects.get_or_create(user=profile_user)

    if created:
        message_info = 'Welcome to your profile! Quickly update your profile picture and details'
        message.info(request, message_info)

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
        id_suggester = Participation.objects.get(name = "post debate topics")
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
                'profile_user_name':profile_user_name, 'created':created}
    return render(request, 'account/profile.html', context)

@login_required
def mod_debate(request, post_id):
    related_post = get_object_or_404(PostDebate, id = post_id)
    debaters_supporting = PostDebater.objects.filter(post=related_post).filter(debate_position="supporting")
    debaters_opposing = PostDebater.objects.filter(post=related_post).filter(debate_position="opposing")

    if request.method == 'POST':
        mod_form = ModeratorForm(request.POST, instance=related_post)
        if mod_form.is_valid():
            mod_form.save()
            messages.success(request, 'Date Changes applied.')
            return redirect('debate:debate_detail', category =related_post.debate_category, \
                    post_id = related_post.pk, post_slug = related_post.slug)
        else:
            messages.error(request, _('Date update failed. Dates are invalid.'))
    else:
        mod_form = ModeratorForm(instance=related_post)
    context = {'mod_form': mod_form, 'related_post':related_post, 'debaters_supporting':debaters_supporting,\
    'debaters_opposing':debaters_opposing, }
    return render(request, 'debate/form/mod_panel.html', context)



@login_required
def score_debate(request, post_id):
    scored = False
    calculated = False
    related_post = get_object_or_404(PostDebate, id = post_id)
    status = Scores.objects.filter(post = related_post).exists()
    if not status:
        if request.method == 'POST':
            score_form = ScoresForm(request.POST)
            if score_form.is_valid():
                post = score_form.save(commit=False)
                post.post = related_post
                post.save()
                scored = "Yes"
                messages.success(request, 'Debate score updated successfully')
                return render(request, 'debate/form/score.html', {'post': post, 'scored':scored})
            else:
                print (score_form.errors)
        else:
            #Display form when scores is yet to be submitted
            score_form = ScoresForm()
            context = {'score_form': score_form, 'scored': scored, 'related_post' : related_post }
            return render(request, 'debate/form/score.html', context )
    elif related_post.debate_category == "open" or status:
        post = get_object_or_404(Scores, post = related_post)
        #Get total votes for both sides
        total_support_vote = Votes.objects.filter(post = related_post).filter(support = True).count()
        total_oppose_vote = Votes.objects.filter(post = related_post).filter(oppose = True).count()

        post.supporting_vote = total_support_vote
        post.opposing_vote = total_oppose_vote
        post.save()

        scored = "Yes"

        judge_support_percent = judge_oppose_percent = total_votes = vote_support_percent = vote_oppose_percent = 0
        supporting_team_percent_score = opposing_team_percent_score = 0
        #calculating Winner

        if related_post.end <= timezone.now(): #check if debate has ended before calculating scores
            if related_post.debate_category == "closed":
                #Assuming debate is closed and judges are to give verdict
                judge_support_percent = (post.supporting_score / post.highest_score) * post.judge_percent_share
                judge_oppose_percent = (post.opposing_score / post.highest_score) * post.judge_percent_share
                total_votes = post.supporting_vote + post.opposing_vote
                vote_support_percent = (post.supporting_vote / total_votes) * post.vote_percent_share
                vote_oppose_percent = (post.opposing_vote / total_votes) * post.vote_percent_share
            else:
                #Assuming debate is open, no judges, winner based on votes only
                total_votes = post.supporting_vote + post.opposing_vote
                vote_support_percent = (post.supporting_vote / total_votes) * 100
                vote_oppose_percent = (post.opposing_vote / total_votes) * 100
            supporting_team_percent_score = vote_support_percent + judge_support_percent
            opposing_team_percent_score = vote_oppose_percent + judge_oppose_percent
            calculated = True

            if not related_post.winner_updated:
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
            #stats_update = Stat.objects.filter()
        context = {'scored': scored, 'calculated': calculated, 'post': post, 'related_post':related_post,
         'judge_support_percent': judge_support_percent, 'judge_oppose_percent':judge_oppose_percent,
         'total_votes':total_votes, 'vote_support_percent': vote_support_percent,
         'vote_oppose_percent': vote_oppose_percent,
         'supporting_team_percent_score': supporting_team_percent_score, 'opposing_team_percent_score':opposing_team_percent_score }

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
        'profile_form': profile_form
    })

def see_badge(request):

    post = Badge.objects.all()

    return render(request, 'debate/post/badge.html', {
        'post':post
    })


def rules_guidelines(request):
    return render(request, 'debate/post/rules_guidelines.html', { })


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

import base64
from django.conf import settings

@require_POST
def load_image(request):
    if request.method == 'POST':
        post_id = int(request.POST.get('post_id', None))
        image_id = int(request.POST.get('image_id', None))

        post = get_object_or_404(PostDebate, pk=post_id)
        attachment = get_object_or_404(Attachment, pk=image_id)
        attachment = settings.MEDIA_ROOT +"/"+ str(attachment)


        with open(attachment, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        return HttpResponse(encoded_string)

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


# from django_comments_xtd import (get_form, comment_was_posted, signals, signed,
#                                  get_model as get_comment_model)
# XtdComment = get_comment_model()
# from django_comments_xtd.forms import XtdCommentForm
# @login_required
# def edit_own_comment(request, comment_id):
#     comment = get_object_or_404(get_comment_model(),
#                                 pk=comment_id, site__pk=settings.SITE_ID)
#
#     #form = get_comment_model
#     form = XtdCommentForm(comment.content_object, comment = comment)
#     #form = get_form()(comment.content_object)
#     print(comment)
#     template_arg = 'comments/edit_comment_form.html'
#     return render(request, template_arg,
#                   {"comment": comment, "form": form, "cid": comment_id})
from django_comments_xtd import (comment_was_posted, signals, signed, get_model )

@login_required
def delete_my_comment(request, comment_id, next=None):
    comment = get_object_or_404(get_model(), pk=comment_id, site__pk=settings.SITE_ID)
    if comment.user == request.user:
        if request.method == "POST":
            comment.is_removed = True
            comment.save()
            post_id = comment.object_pk
            post_model = comment.content_type.model

            return redirect(comment.content_object.get_absolute_url())
        else:
            return render(request, 'comments/delete.html', {'comment': comment, "next": next}, )
    else:
        raise Http404
