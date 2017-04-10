# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-09 23:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='url_title',
            field=models.TextField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.TextField(max_length=255),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.TextField(max_length=40),
        ),
    ]
