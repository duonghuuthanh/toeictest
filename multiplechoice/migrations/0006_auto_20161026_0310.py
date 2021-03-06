# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 03:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplechoice', '0005_auto_20161025_1103'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='title',
            new_name='subject',
        ),
        migrations.AddField(
            model_name='message',
            name='sent',
            field=models.PositiveSmallIntegerField(choices=[(0, 'An email has not sent yet'), (1, 'An email sent')], default=1),
        ),
        migrations.AddField(
            model_name='message',
            name='sent_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
