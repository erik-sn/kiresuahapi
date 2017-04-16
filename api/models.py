from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    modified = models.DateTimeField(auto_now=True, blank=False, null=False)
    title = models.TextField(blank=False, null=False, max_length=255)
    url_title = models.TextField(blank=False, null=False, max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=False)
    tags = models.ManyToManyField('Tag', blank=True)
    owner = models.ForeignKey(User, blank=False, null=False)
    published = models.BooleanField(default=False, null=False, blank=False)


class Tag(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    modified = models.DateTimeField(auto_now=True, blank=False, null=False)
    name = models.TextField(blank=False, null=False, max_length=40)

