from django.db import models
from taggit.managers import TaggableManager

class Exercice(models.Model):
#    question_text = models.CharField(max_length=200)
    enonce_text = models.TextField()
#    indication_text = models.TextField
    corrige_text = models.TextField(default="pas de correction")
#    id = models.IntegerField
    pub_date = models.DateTimeField('date published')
    tags = TaggableManager()
    def __str__(self):
        return self.enonce_text