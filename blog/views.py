from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BlogPost
from django.contrib.auth.models import User
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

def blog_list(request, tag_slug = None):
    object_list = BlogPost.published.all()
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


    template = 'blog/post/blog_list.html'
    context = {'object_list': object_list, 'tag':tag, 'meta':meta, }

    return render(request, template , context)

def blog_detail(request, post_id, post_slug):
    post = get_object_or_404(BlogPost, id=post_id)
    user_id = request.user.pk

    context = {'post':post, 'meta':meta }

    return render(request, 'blog/post/blog_detail.html', context)
