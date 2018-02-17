# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-17 20:27
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import martor.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Give a clear title for the post', max_length=250)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('show', models.BooleanField(default=True, verbose_name='BlogPost Enabled/Disabed')),
                ('body', martor.models.MartorField(verbose_name='Body of the blog post')),
                ('allow_comments', models.BooleanField(default=True, verbose_name='allow comments')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(blank=True, default=django.contrib.auth.models.User, on_delete=django.db.models.deletion.CASCADE, related_name='blogauthor', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]