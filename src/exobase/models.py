from django.db import models
from taggit.managers import TaggableManager
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User

class Exercice(models.Model):
    enonce_text = models.TextField()
#    indication_text = models.TextField
    corrige_text = models.TextField(default="pas de correction")
#    id = models.IntegerField
    pub_date = models.DateTimeField('date published')
    tags = TaggableManager()
   # author = ForeignKey(User)
    def __str__(self):
        return self.enonce_text