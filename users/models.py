from __future__ import unicode_literals

from uuid import uuid4

from django.db import models
# Create your models here.
from django.template.defaultfilters import urlencode


def f():
    d = uuid4()
    str = d.hex
    return urlencode(str[0:16])


class AppUser(models.Model):
    _id = models.CharField(max_length=16, default=f, unique=True)
    fbid = models.CharField(max_length=200, )


class Reading(models.Model):
    user = models.ForeignKey('AppUser')
    product = models.CharField(max_length=40)
    calories = models.FloatField()
    timestamp = models.DateTimeField(primary_key=True)
