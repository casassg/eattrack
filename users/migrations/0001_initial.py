# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 01:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('_id', models.AutoField(primary_key=True, serialize=False)),
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