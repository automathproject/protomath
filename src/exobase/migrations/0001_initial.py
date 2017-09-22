# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('enonce_text', models.TextField()),
                ('corrige_text', models.TextField(default='pas de correction')),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', help_text='A comma-separated list of tags.', through='taggit.TaggedItem', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderFolder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('number', models.PositiveIntegerField()),
                ('exercice', models.ForeignKey(to='exobase.Exercice')),
                ('folder', models.ForeignKey(to='exobase.Folder')),
            ],
        ),
        migrations.AddField(
            model_name='folder',
            name='exercices',
            field=models.ManyToManyField(to='exobase.Exercice', related_name='in_folder', through='exobase.OrderFolder'),
        ),
    ]
