# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-10 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exobase', '0005_solution_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]