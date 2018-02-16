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
    return render(request, '404.html' )

def handler500(request):
    return render(request, '500.html' )


# def handler404(request):
#     message_info = "An error occured while opening your page. Please try Again."
#     messages.info(request, message_info )
#     return redirect('all_list', permanent=True )
#
# def handler500(request):
#     message_info = "An error occured while opening your page. Please try Again."
#     messages.info(request, message_info )
#     return redirect('all_list', permanent=True )

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

#A function to get the ip host of logged in user
#Used to track activities and get total user views
from ipware import get_client_ip

def client_ip(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        return "127.0.0.1" #A default IP as a dummy
    else:
        return client_ip

def post_detail(request, post_id, post_slug):
    post = get_object_or_404(Post, id=post_id)
    similar_posts = post.tags.similar_objects()[:5] #Get five other similar posts
    user_id = request.user.pk
    post_form = PostForm()

    ip_add = client_ip(request) #gets user ip address
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
    context = {'post':post, 'like_count':like_count, 'liked':liked, 'post_form':post_form, 'meta':meta, 'similar_posts':similar_posts }

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
            post = form.save(commit=False)
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
        context =  {'form': form, 'post_id':post_id, 'meta':meta}
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


import os
import json
import uuid

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from martor.utils import LazyEncoder

@login_required
def markdown_uploader(request):
    """
    Makdown image upload for locale storage
    and represent as json to markdown editor.
    """
    if request.method == 'POST' and request.is_ajax():
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_MB = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size) MB.') % {'size': to_MB}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
            def_path = default_storage.save(tmp_file, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, def_path)
            
            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))
