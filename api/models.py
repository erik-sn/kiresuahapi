from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Article(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    created = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='edited')
    title = models.TextField(blank=False, null=False, db_column='title')
    description = models.TextField(blank=True, null=True, db_column='description')
    content = models.TextField(blank=True, null=True, db_column='content')
    tags = models.ManyToManyField('Tag', blank=True)
    owner = models.ForeignKey(User, blank=False, null=False, default=1, db_column='owner')
    published = models.BooleanField(default=False, null=False)

    class Meta:
        managed = True
        db_table = 'articles'


class Tag(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    created = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='edited')
    name = models.TextField(blank=False, null=False, db_column='name')

    class Meta:
        managed = True
        db_table = 'tags'
