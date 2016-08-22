from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User


class ToDo(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    title = models.TextField(blank=False, null=False, db_column='name')
    description = models.TextField(blank=True, null=True, db_column='description')
    created = models.DateTimeField(default=timezone.now, blank=True, null=True, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=True, null=True, db_column='modified')

    class Meta:
        managed = True
        db_table = 'todos'

    def __str__(self):
        return 'Title: {} Description: {} Create Date: {} Modify Date: {} Active: {}'\
            .format(self.title, self.description, self.created, self.modified)


class Markup(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    user = models.ForeignKey(User, db_column='user', blank=False, null=False)
    title = models.TextField(blank=False, null=False, db_column='title')
    description = models.TextField(blank=True, null=True, db_column='description')
    text = models.TextField(blank=True, null=True, db_column='text')
    created = models.DateTimeField(default=timezone.now, blank=True, null=True, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=True, null=True, db_column='modified')

    class Meta:
        managed = True
        db_table = 'markups'

    def __str__(self):
        return 'Title: {} Description: {} Text: {} User: {} Create Date: {} Modify Date: {} '\
            .format(self.title, self.description, self.text, self.user, self.created, self.modified)


class PortfolioMessage(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.TextField(blank=True, null=True, db_column='name')
    email = models.TextField(blank=True, null=True, db_column='email')
    phoneNumber = models.TextField(blank=True, null=True, db_column='phonenumber')
    message = models.TextField(blank=True, null=True, db_column='message')
    created = models.DateTimeField(default=timezone.now, blank=True, null=True, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=True, null=True, db_column='modified')

    class Meta:
        managed = True
        db_table = 'portfoliomessages'

    def __str__(self):
        return 'Name: {} Email: {} Number: {} Message: {} Create Date: {}'\
            .format(self.name, self.email, self.phoneNumber, self.message, self.created)


class Entry(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    created = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='edited')
    title = models.TextField(blank=False, null=False, db_column='title')
    description = models.TextField(blank=True, null=True, db_column='description')
    content = models.TextField(blank=True, null=True, db_column='content')
    tags = models.ManyToManyField('Tag', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'entries'


class Tag(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    created = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='created')
    modified = models.DateTimeField(default=timezone.now, blank=False, null=False, db_column='edited')
    name = models.TextField(blank=False, null=False, db_column='name')

    class Meta:
        managed = True
        db_table = 'tags'
