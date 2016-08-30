# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exobase', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercice',
            name='question_text',
            field=models.CharField(max_length=200, default='exo vide'),
            preserve_default=False,
        ),
    ]
