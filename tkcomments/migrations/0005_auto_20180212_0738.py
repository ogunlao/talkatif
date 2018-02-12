# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-12 06:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tkcomments', '0004_auto_20180212_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tkcomment',
            name='comment_anonymous',
            field=models.CharField(blank=True, choices=[('B.Y', 'BE YOURSELF'), ('B.A', 'BE ANONYMOUS')], help_text='comment as anonymous', max_length=12, null=True, verbose_name='Is this comment an anonymous comment'),
        ),
    ]
