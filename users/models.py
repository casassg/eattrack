from __future__ import unicode_literals

from django.db import models

# Create your models here.


class AppUser(models.Model):
    fbid = models.TextField()


class Reading(models.Model):
    user = models.ForeignKey('AppUser')
    food = models.CharField(max_length=40)
