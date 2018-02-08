from django.conf.urls import url

from . import views

urlpatterns = [
    # post views
    url(r'^$', views.blog_list, name='blog_list'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.blog_list, name='blog_list_by_tag'),
    url(r'^(?P<post_id>\d+)/(?P<post_slug>[-\w]+)/$', views.blog_detail, name='blog_detail'),

]
