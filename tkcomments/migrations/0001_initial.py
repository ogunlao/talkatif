# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-09 18:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_comments_xtd', '0005_auto_20170920_1247'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TkComment',
            fields=[
                ('xtdcomment_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='django_comments_xtd.XtdComment')),
                ('comment_anonymous', models.CharField(blank=True, choices=[('BE YOURSELF', 'BE YOURSELF'), ('BE ANONYMOUS', 'BE ANONYMOUS')], help_text='comment as anonymous', max_length=12, null=True, verbose_name='Is this comment an anonymous comment')),
                ('anonymous_user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='anonymous_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'comments',
                'verbose_name': 'comment',
                'abstract': False,
                'ordering': ('submit_date',),
                'permissions': [('can_moderate', 'Can moderate comments')],
            },
            bases=('django_comments_xtd.xtdcomment',),
        ),
    ]