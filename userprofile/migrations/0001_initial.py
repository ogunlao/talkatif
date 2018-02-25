# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-25 21:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other_name', models.CharField(blank=True, max_length=100, null=True)),
                ('specialization', models.CharField(blank=True, help_text='e.g. Practicing Lawyer,                                             Programmer, Business Man, Political Activist', max_length=200, null=True)),
                ('date_of_birth', models.DateField(blank=True, help_text='yyyy/mm/dd', null=True)),
                ('bio', models.TextField(blank=True, help_text='Tell us a little about yourself.', null=True)),
                ('city', models.CharField(blank=True, help_text='e.g Lagos, New York', max_length=100, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('notify', models.BooleanField(default=True, help_text='Notify me of upcoming debates.')),
                ('gender', models.CharField(blank=True, choices=[('male', 'male'), ('female', 'female')], max_length=6, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
