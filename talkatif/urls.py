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
from django.views.generic import RedirectView
from stream import views


urlpatterns = [
    url(r'^$', views.index, name = 'main_page'),
    #url(r'^$', RedirectView.as_view(url='/all/', permanent=True)),
    url(r'^all/', views.all_list, name='all_streams'),
    url(r'^admin/', admin.site.urls),
    url(r'^debate/', include('stream.urls', namespace='stream', app_name='stream')),
    url(r'^opine/', include('opine.urls', namespace='opine', app_name='opine')),
    url(r'^index/', views.index, name = 'index'),
    url(r'^search/', include('haystack.urls')),
    url(r'^blog/', include('zinnia.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/(?P<username>[-\w\d]+)/', views.profile, name='profile'),
    url(r'^accounts/profile/', views.update_profile, name='update_profile'),
    url(r'^dashboard/', views.dashboard, name = 'dashboard'),
]

handler404 = 'opine.views.handler404'
handler500 = 'opine.views.handler500'
# Use static() to add url mapping to serve static files during development (only)

from django.conf.urls.static import static
from django.conf import settings

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
