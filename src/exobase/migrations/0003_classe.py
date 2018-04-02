# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-05 16:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exobase', '0002_auto_20170905_1620'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50)),
                ('year', models.CharField(blank=True, max_length=9)),
                ('eleves', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]