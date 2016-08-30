from django.db import models

class Exercice(models.Model):
    enonce_text = models.TextField
    indication_text = models.TextField
    corrige_text = models.TextField
    id = models.IntegerField
    pub_date = models.DateTimeField('date published')
    
