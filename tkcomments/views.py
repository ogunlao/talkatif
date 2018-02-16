from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from meta.views import Meta #to include metatags in view for display, check django-meta
from django.contrib import messages
from django_comments_xtd import (comment_was_posted, signals, signed, get_model )
from .forms import CommentForm
from django.utils import timezone
from django.utils.http import is_safe_url

#Default meta details for post
meta = Meta(
    title="Welcome to Talkatif. Home to debates, opinions, arguments and talks. A talking family.",
    description="talkatif.com creates an environment for interesting talks, debates, arguments and opinions.",
    url="/",
    extra_props = {
        #'viewport': 'width=device-width, initial-scale=1.0, minimum-scale=1.0'
    }
)

@login_required
def edit_my_comment(request, comment_id):
    comment = get_object_or_404(get_model(),
                                pk=comment_id, site__pk=settings.SITE_ID)
    redirect_to = request.GET.get('next', '/all/')
    if comment.user == request.user:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                # Form fields passed validation
                comment_value = form.cleaned_data['comment']
                comment.comment = comment_value
                comment.submit_date = timezone.now()
                comment.save()
                messages.info(request, 'Comment updated successfully.')
                if is_safe_url(url=redirect_to, host=request.get_host()):
                    return HttpResponseRedirect(redirect_to)
        else:
            form = CommentForm(instance=comment)
        template_arg = 'edit_comment.html'
        return render(request, template_arg,
                      {"comment": comment,"form": form, "cid": comment_id, "next": next})
    else:
        raise Http404

@login_required
def remove_my_comment(request, comment_id, next=None):
    comment = get_object_or_404(get_model(), pk=comment_id, site__pk=settings.SITE_ID)
    if comment.user == request.user:
        if request.method == "POST":
            comment.is_removed = True
            comment.save()
            post_id = comment.object_pk
            post_model = comment.content_type.model
            return redirect(comment.content_object.get_absolute_url())
        else:
            return render(request, 'comments/delete.html', {'comment': comment, 'next': next, 'meta':meta}, )
    else:
        raise Http404
