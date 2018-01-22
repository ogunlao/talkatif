from stream.models import PostDebate
from opine.models import Post
from django import forms
from django.contrib.auth.models import User

# -*- encoding: utf-8 -*-
from dashing.widgets import NumberWidget
from random import randint

users = User.objects.all().count()


class TotalUsersWidget(NumberWidget):
    title = 'Total Users'
    value = users

    def get_more_info(self):
        more_info = 'It indicates the total number of registered users.'
        return more_info

    def get_value(self):
        global users
        return users

    def get_detail(self):
        global users
        return 'Total Users Since Start - {}'.format(users)
