from django.conf.urls import url

from . import views

urlpatterns = [
    # post views
    url(r'^$', views.post_list, name='post_list'),
    #url(r'^(?P<category>\w+)/$', views.post_list, name='post_list_by_category'),
    url(r'^edit/(?P<post_id>\d+)/$', views.new_post, name='edit_post'),
    url(r'^new/$', views.new_post, name='new_post'),
    url(r'^like-post/$', views.like_post, name='like-post'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list, name='post_list_by_tag'),
    url(r'^(?P<post_id>\d+)/(?P<post_slug>[-\w]+)/$', views.post_detail, name='post_detail'),
    url(r'^(?P<post_id>\d+)/(?P<post_slug>[-\w]+)/$', views.go_to_post, name='goto_post_page'),
]
