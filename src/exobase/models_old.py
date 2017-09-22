from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.utils import timezone

class Exercice(models.Model):
    enonce_text = models.TextField()
#    indication_text = models.TextField
    corrige_text = models.TextField(default="pas de correction")
#    id = models.IntegerField
    pub_date = models.DateTimeField('date published')
    tags = TaggableManager()
    author = models.ForeignKey(User)
    
    def __str__(self):
        return str(self.id)
    
class Folder(models.Model):
    exercices = models.ManyToManyField(Exercice, related_name='in_folder', through='OrderFolder')
    name = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published',default=timezone.now, blank=True)
    author = models.ForeignKey(User)
    
    def __str__(self):
        return self.name
    
    def get_exercice(self):
        return self.exercices.order_by('link_to_folder')
    
    def count_exercice(self):
        return self.exercices.count()

class OrderFolder(models.Model):
    number = models.PositiveIntegerField()
    exercice = models.ForeignKey(Exercice, related_name='link_to_folder')
    folder = models.ForeignKey(Folder)
    
    def __str__(self):
        return str(self.number)+'-'+str(self.exercice.id)