from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    modified = models.DateTimeField(auto_now=True, blank=False, null=False)
    title = models.TextField(blank=False, null=False, max_length=255)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    owner = models.ForeignKey(User, blank=False, null=False)


class Tag(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    modified = models.DateTimeField(auto_now=True, blank=False, null=False)
    name = models.TextField(blank=False, null=False, max_length=40)

