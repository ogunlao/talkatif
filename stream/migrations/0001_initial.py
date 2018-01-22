# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-01-22 15:02
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import taggit.managers
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', versatileimagefield.fields.VersatileImageField(blank=True, help_text='Add Pictures', null=True, upload_to='attachments/stream', verbose_name='Image Attachments')),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('rank', models.PositiveSmallIntegerField()),
                ('wins', models.PositiveIntegerField(blank=True, default=0)),
                ('loose', models.PositiveIntegerField(blank=True, default=0)),
                ('suggested', models.PositiveIntegerField(blank=True, default=0)),
                ('moderated', models.PositiveIntegerField(blank=True, default=0)),
                ('judged', models.PositiveIntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Notifyme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notified', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Notify Me',
            },
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostDebate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of Debate', max_length=500)),
                ('slug', models.SlugField(max_length=250, unique_for_date='created')),
                ('show', models.BooleanField(default=True, verbose_name='Can debate be viewed online ?')),
                ('debate_category', models.CharField(choices=[('open', 'open'), ('closed', 'closed')], default='open', max_length=6)),
                ('status', models.CharField(choices=[('st', 'started'), ('end', 'ended')], default='st', max_length=3)),
                ('summary', models.TextField(help_text="Enter a brief summary. <a href='http://commonmark.org/help/' target='_blank'>Markdown supported<a/>", max_length=1000, verbose_name='What is your inspiration for the debate?')),
                ('allow_comments', models.BooleanField(default=True, verbose_name='allow comments')),
                ('begin', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('vote_starts', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('stats_updated', models.BooleanField(default=False, verbose_name='Has Statistics been updated')),
                ('winner_updated', models.BooleanField(default=False, verbose_name='Has winner been declared')),
                ('debate_notification', models.BooleanField(default=False, verbose_name='Has debaters, moderators and judges been notified')),
                ('winner', models.CharField(blank=True, choices=[('supporting', 'Supporting Team'), ('opposing', 'Opposing Team'), ('draw', 'It was a tie'), ('InProgress', 'In Progress')], default='InProgress', max_length=10, null=True)),
                ('count', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='suggested_post', to=settings.AUTH_USER_MODEL)),
                ('judges', models.ManyToManyField(blank=True, help_text='Select judges', related_name='judge_team', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('moderator', models.ManyToManyField(help_text='Select moderators', related_name='debate_moderator', to=settings.AUTH_USER_MODEL)),
                ('opposing_debaters', models.ManyToManyField(blank=True, help_text='Select the opposing team', related_name='opposing_team', to=settings.AUTH_USER_MODEL)),
                ('supporting_debaters', models.ManyToManyField(blank=True, help_text='Select the supporting team', related_name='supporting_team', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='PostDebater',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debate_position', models.CharField(choices=[('opposing', 'Opposing'), ('supporting', 'Supporting'), ('judge', 'Judge'), ('moderator', 'Moderator')], max_length=10)),
                ('approval_status', models.BooleanField(default=False, verbose_name='Approval Status')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.PostDebate')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('specialization', models.CharField(blank=True, help_text='e.g. Practicing Lawyer,                                             Programmer, Business Man, Political Activist', max_length=200, null=True)),
                ('date_of_birth', models.DateField(blank=True, help_text='yyyy/mm/dd', null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('mobile_no', models.CharField(blank=True, max_length=11, null=True)),
                ('city', models.CharField(blank=True, help_text='e.g Lagos, New York', max_length=100, null=True)),
                ('country', django_countries.fields.CountryField(default='NG', max_length=2)),
                ('notify', models.BooleanField(default=True, help_text='Notify me of upcoming debates.')),
                ('image', versatileimagefield.fields.VersatileImageField(blank=True, height_field='height', null=True, upload_to='images/profile/', verbose_name='Image', width_field='width')),
                ('height', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image Height')),
                ('width', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image Width')),
                ('optional_image', versatileimagefield.fields.VersatileImageField(blank=True, upload_to='images/profile/optional/', verbose_name='Optional Image')),
                ('participation_type', models.ManyToManyField(blank=True, related_name='participation_type', to='stream.Participation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Scores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supporting_score', models.SmallIntegerField(blank=True, default=0, help_text='Score for Supporting Side on a scale of 10', validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('opposing_score', models.SmallIntegerField(blank=True, default=0, help_text='Score for Opposing Side on a scale of 10', validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('highest_score', models.PositiveSmallIntegerField(blank=True, default=10, help_text='Highest Possible Score Possible')),
                ('observation', models.TextField(blank=True, help_text='If anomalies observed or comments, write here', max_length=1000, null=True)),
                ('supporting_vote', models.PositiveIntegerField(blank=True, default=0)),
                ('opposing_vote', models.PositiveIntegerField(blank=True, default=0)),
                ('vote_percent_share', models.PositiveSmallIntegerField(blank=True, default=70)),
                ('judge_percent_share', models.PositiveSmallIntegerField(blank=True, default=30)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.PostDebate')),
            ],
            options={
                'verbose_name_plural': 'Scores',
            },
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supported', models.BooleanField(default=False)),
                ('opposed', models.BooleanField(default=False)),
                ('moderated', models.BooleanField(default=False)),
                ('judged', models.BooleanField(default=False)),
                ('won', models.BooleanField(default=False)),
                ('lost', models.BooleanField(default=False)),
                ('drew', models.BooleanField(default=False)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.PostDebate')),
            ],
        ),
        migrations.CreateModel(
            name='Suggest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('summary', models.TextField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, default=django.contrib.auth.models.User, on_delete=django.db.models.deletion.CASCADE, related_name='suggester', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='TrackedBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('award_date', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.Badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-award_date',),
            },
        ),
        migrations.CreateModel(
            name='TrackedPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=16)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.PostDebate')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Votes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('support', models.NullBooleanField(default=False)),
                ('oppose', models.NullBooleanField(default=False)),
                ('voting_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.PostDebate')),
                ('voter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Votes',
            },
        ),
        migrations.AddField(
            model_name='notifyme',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stream.PostDebate'),
        ),
        migrations.AddField(
            model_name='notifyme',
            name='user_notify',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_to_nofify', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='badge',
            name='category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='stream.Participation'),
        ),
        migrations.AddField(
            model_name='badge',
            name='collected_by',
            field=models.ManyToManyField(blank=True, related_name='collected_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attachment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachment', to='stream.PostDebate'),
        ),
    ]
