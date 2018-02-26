from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from .forms import UserForm, ProfileForm
from meta.views import Meta
from django.contrib.auth.models import User
from .models import Profile
# Create your views here.
from django.db import transaction
from django.utils.translation import gettext as _

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
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    post, created = Profile.objects.get_or_create(user=profile_user)

    profile_user_name = profile_user.get_full_name()

    context = {'post': post, 'profile_user': profile_user, 'meta':meta}
    return render(request, 'account/profile.html', context)
