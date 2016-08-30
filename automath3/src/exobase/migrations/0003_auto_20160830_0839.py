# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exobase', '0002_exercice_question_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exercice',
            name='question_text',
        ),
        migrations.AddField(
            model_name='exercice',
            name='enonce_text',
            field=models.TextField(default='exo vide'),
            preserve_default=False,
        ),
    ]
