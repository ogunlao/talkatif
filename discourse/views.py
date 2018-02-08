from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Post, TrackedPost
from .forms import PostForm
from django.contrib.auth.models import User
#from .forms import PostDebateForm
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from meta.views import Meta #to include metatags in view for display, check django-meta
from taggit.models import Tag
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from markdownx.forms import ImageForm

#Default meta details for post
meta = Meta(
    title="Welcome to Talkatif. Home to debates, opinions, arguments and talks. A talking family.",
    description="talkatif.com creates an environment for interesting talks, debates, arguments and opinions.",
    url="/",
    extra_props = {
        #'viewport': 'width=device-width, initial-scale=1.0, minimum-scale=1.0'
    }
)

def handler404(request):
    message_info = "An error occured while opening your page. Please try Again."
    messages.info(request, message_info )
    return redirect('all_list', permanent=True )

def handler500(request):
    message_info = "An error occured while opening your page. Please try Again."
    messages.info(request, message_info )
    return redirect('all_list', permanent=True )

def post_list(request, tag_slug = None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        try:
            tag = Tag.objects.all().get(slug=tag_slug)
            object_list = object_list.filter(tags__in=[tag])
        except:
            pass

    paginator = Paginator(object_list, 50) # Show 50 posts per page

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    except EmptyPage:
        page = paginator.num_pages

    object_list = paginator.page(page)


    template = 'discourse/post/post_list.html'
    context = {'object_list': object_list, 'tag':tag, 'meta':meta, }

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

def post_detail(request, post_id, post_slug):
    post = get_object_or_404(Post, id=post_id)
    user_id = request.user.pk
    post_form = PostForm()

    ip_add = get_client_ip(request) #gets user ip address
    if request.user.is_authenticated(): #To save user data for page views
        request_user = request.user
    else: request_user = None
    #Create the user in the database if not found, added to total views number
    tracked_post, created = TrackedPost.objects.get_or_create(post=post, ip=ip_add, user=request_user) #note, not actual api
    if created:
        tracked_post.post.count += 1 #increases count on post
        tracked_post.post.save()

    liked = False
    #Checks if user have liked post before
    for person in post.likes.all():
        if person == request_user:
            liked = True
            break

    like_count = post.total_likes #counts total likes on post
    context = {'post':post, 'like_count':like_count, 'liked':liked, 'post_form':post_form, 'meta':meta }

    return render(request, 'discourse/post/post_detail.html', context)


@login_required
def new_post(request, post_id = None):
    post = Post()
    if post_id: #if instance of post is to be edited
        post = get_object_or_404(Post, pk = post_id)

    if request.method == 'POST':
        # Form was submitted
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            # Form fields passed validation
            post = form.save(commit=False)
            if request.FILES:
                image_form = ImageForm(request.POST, request.FILES)
                if image_form.is_valid:
                    file = image_form.save()
                    if file:
                        image_tag = "\n\n![](" + file +")\n"
                        post.summary = post.summary + image_tag

            post.author = request.user

            try:
                post.save()
                form.save_m2m()
            except IntegrityError as e:
                if 'unique constraint' in e.args[0]: # or e.args[0] from Django 1.10
                    message_info = "Post has previously been saved."
                    messages.info(request, message_info )
                return redirect('all_list')

            post = get_object_or_404(Post, title = post.title )

            message_info = "Post saved! Come back for comments and responses."
            messages.info(request, message_info )
            post = get_object_or_404(Post, title = post.title )
            return redirect('discourse:post_detail', post_id=post.id, post_slug = post.slug )
        else:
            messages.info(request, "We encourage a maximum of 2 images per post." )
    else:
        form = PostForm(instance=post)
        image_form = ImageForm()
        context =  {'form': form, 'post_id':post_id, 'image_form':image_form, 'meta':meta}
        return render(request, 'discourse/form/new_post.html', context)

from django.http import HttpResponse
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.views.decorators.http import require_POST

@login_required
@require_POST
def like_post(request):
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        post = get_object_or_404(Post, slug=slug)
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

def go_to_post(request, post_slug):
    goto_page_no = request.GET.get('goto')
    try:
        goto_page_no = int(goto_page_no)
    except ValueError:
        goto_page_no = 1
    url = "reverse('discourse:go_to_post', kwargs={'post_id':post_id, 'post_slug':post_slug, 'goto_page_no':goto_page_no})"
    return HttpResponseRedirect('url')
