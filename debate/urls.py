from django.conf.urls import url

from . import views


urlpatterns = [
    # postdebate views
    url(r'^$', views.debate_list, name='debate_list'),
    url(r'^mod/(?P<post_id>\d+)/$', views.mod_debate, name='mod_debate'), #to score debates
    url(r'^like/$', views.like, name='like'),
    url(r'^notify/$', views.notify, name='notify'),
    url(r'^vote/$', views.vote, name='vote'),
    url(r'^approve/$', views.approve, name='approve'),
    url(r'^load_image/$', views.load_image, name='load_image'),
    url(r'^badge/$', views.see_badge, name='see_badge'),
    url(r'^rules_guidelines/$', views.rules_guidelines, name='rules_guidelines'),
    url(r'^newpost/$', views.new_post, name='suggest_post'),
    url(r'^edit/(?P<post_id>\d+)/$', views.new_post, name='edit_debate_post'),
    url(r'^join/(?P<post_id>\d+)/(?P<position>\w+)',views.join_participants, name='join_participants'),
    url(r'^(?P<category>\w+)/$', views.debate_list, name='debate_list_by_category'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.debate_list, name='debate_list_by_tag'), #displays list according to tag
    url(r'^(?P<category>\w+)/(?P<post_id>\d+)/(?P<post_slug>[-\w]+)/$', views.debate_detail, name='debate_detail'),
    url(r'^(?P<category>\w+)/(?P<post_id>\d+)/(?P<post_slug>[-\w]+)/$', views.go_to, name='goto_page'),



    url(r'^score/(?P<post_id>\d+)/$', views.score_debate, name='score_debate'), #to change time and date of debates


]
