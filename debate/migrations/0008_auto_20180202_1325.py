# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-02 12:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('debate', '0007_auto_20180201_0813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='post',
        ),
        migrations.DeleteModel(
            name='Attachment',
        ),
    ]
