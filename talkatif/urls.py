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
from debate import views as debate_views
from discourse import views as discourse_views

#sitemap url config
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, PostSitemap, PostDebateSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'post': PostSitemap,
    'postdebate' : PostDebateSitemap,
}

urlpatterns = [
    url(r'^$', debate_views.index, name = 'main_page'),
    url(r'^all/', debate_views.all_list, name='all_list'),
    url(r'^search/', include('haystack.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^debate/', include('debate.urls', namespace='debate', app_name='debate')),
    url(r'^discourse/', include('discourse.urls', namespace='discourse', app_name='discourse')),
    url(r'^index/', debate_views.index, name = 'index'),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^profile/deactivate/$', debate_views.deactivate_profile, name='deactivate_profile'),
    url(r'^faq/$', debate_views.faq, name='faq'),
    url(r'^delete_comment/(?P<comment_id>\d+)/$', debate_views.delete_my_comment, name='delete_my_comment'),
    url(r'^blog/', include('blog.urls', namespace='blog', app_name='blog')),
    url(r'^attachment/', include('markdownx.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/(?P<username>[-\w\d]+)/', debate_views.profile, name='profile'),
    url(r'^accounts/profile/', debate_views.update_profile, name='update_profile'),
    url(r'^dashboard/', debate_views.dashboard, name = 'dashboard'),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
    name='django.contrib.sitemaps.views.sitemap'),
]

handler404 = 'discourse.views.handler404'
handler500 = 'discourse.views.handler500'
# Use static() to add url mapping to serve static files during development (only)

from django.conf.urls.static import static
from django.conf import settings

#if settings.DEBUG == True:
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
