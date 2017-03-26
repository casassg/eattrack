from __future__ import unicode_literals

from django.db import models


# Create your models here.

class AppUser(models.Model):
    _id = models.AutoField(primary_key=True)
    fbid = models.CharField(max_length=200)


class Reading(models.Model):
    user = models.ForeignKey('AppUser')
    product = models.CharField(max_length=40)
    calories = models.FloatField()
    timestamp = models.DateTimeField(primary_key=True)
