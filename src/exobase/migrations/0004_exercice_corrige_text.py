# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exobase', '0003_auto_20160830_0839'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercice',
            name='corrige_text',
            field=models.TextField(default='pas de correction'),
        ),
    ]
