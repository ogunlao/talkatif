"""talkatif URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib import auth

# Use include() to add URLS from the catalog application
from django.conf.urls import include

#Add URL maps to redirect the base URL to our application
from discourse import views as discourse_views
from userprofile import views as userprofile_views
from tkcomments import views as tk_views
#sitemap url config
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, PostSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'post': PostSitemap,
}

from django.conf.urls.static import static
from django.conf import settings

# urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    url(r'^$', discourse_views.index, name = 'main_page'),
    url(r'^all/', discourse_views.all_list, name='all_list'),
    url(r'^search/', include('haystack.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^talk/', include('discourse.urls', namespace='discourse', app_name='discourse')),
    url(r'^index/', discourse_views.index, name = 'index'),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^attachment/uploader/$', discourse_views.markdown_uploader, name='markdown_uploader_page'),
    url(r'^profile/deactivate/$', userprofile_views.deactivate_profile, name='deactivate_profile'),
    url(r'^faq/$', discourse_views.faq, name='faq'),
    url(r'^comment/remove/(?P<comment_id>\d+)/$', tk_views.remove_my_comment, name='remove_my_comment'),
    url(r'^comment/edit/(?P<comment_id>\d+)/$', tk_views.edit_my_comment, name='edit_my_comment'),
    url(r'^blog/', include('blog.urls', namespace='blog', app_name='blog')),
    url(r'^martor/', include('martor.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/', userprofile_views.update_profile, name='update_profile'),
    url(r'^dashboard/', discourse_views.dashboard, name = 'dashboard'),
    url(r'^(?P<username>[-\w\d]+)/', userprofile_views.profile, name='profile'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
    name='django.contrib.sitemaps.views.sitemap'),
]

handler404 = 'discourse.views.handler404'
handler500 = 'discourse.views.handler500'
