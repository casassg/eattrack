# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 01:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_id', models.CharField(default=users.models.f, max_length=16, unique=True)),
                ('fbid', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('product', models.CharField(max_length=40)),
                ('calories', models.FloatField()),
                ('timestamp', models.DateTimeField(primary_key=True, serialize=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.AppUser')),
            ],
        ),
    ]
