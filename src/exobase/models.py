from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    WORK_TYPES = (
                  ('E','Etudiant'),
                  ('P','Professeur'),
                  ('A','Autre'),
                  )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    organization = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    work = models.CharField(max_length=1, choices=WORK_TYPES)
    website = models.URLField(default='', blank=True)
    avatar = models.ImageField(blank=True)
    
    def __str__(self):
        return 'Profil de '+str(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

    
class MacroLatex(models.Model):
    name = models.CharField(blank=True, max_length=50)
    macro = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Exercice(models.Model):
    VISIBILITY_TYPES = (
            ('A','Public'),
            ('P','Personnalisé'),
                        )
    name = models.CharField(blank=True, max_length=50)
    level = models.CharField(blank=True, max_length=50)
    difficulty = models.DecimalField(max_digits=2,decimal_places=1,default=0)
    popularity = models.DecimalField(max_digits=2,decimal_places=1,default=5)
    quality = models.DecimalField(max_digits=2,decimal_places=1,default=5)
    enonce_latex = models.TextField(blank=True)
    enonce_html = models.TextField(blank=True)
    description = models.TextField(blank=True)
    indication_latex = models.TextField(blank=True)
    indication_html = models.TextField(blank=True)
    macro = models.ForeignKey(MacroLatex, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(blank=True)
    figure = models.TextField(blank=True) #pour insertion d'iframe
    pub_date = models.DateTimeField('date published')
    tags = TaggableManager()
    author = models.ForeignKey(User)
    visibility = models.CharField(max_length=1, choices = VISIBILITY_TYPES, default='A')
    
    def __str__(self):
        return str(self.id)

class Solution(models.Model):
    VISIBILITY_TYPES = (
            ('A','Public'),
            ('P','Personnalisé'),
            )
    quality = models.DecimalField(max_digits=2,decimal_places=1,default=5)   
    enonce_latex = models.TextField(blank=True)
    enonce_html = models.TextField(blank=True)
    macro = models.ForeignKey(MacroLatex, on_delete=models.CASCADE, blank=True, null=True)
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(User)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=1, choices = VISIBILITY_TYPES, default='A')

    def __str__(self):
        return 'Solution de Ex' + str(self.exercice.id)
    


class Comment(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(User)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    def __str__(self):
        return str(self.id)

class Folder(models.Model):
    exercices = models.ManyToManyField(Exercice, related_name='in_folder', through='OrderFolder')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField('date published',default=timezone.now)
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
    
class Collection(models.Model):
    folders = models.ManyToManyField(Folder)
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Classe(models.Model):
    name = models.CharField(blank=True, max_length=50)
    description = models.CharField(blank=True, max_length=50)
    eleves = models.ManyToManyField(User)
    year = models.CharField(blank=True, max_length=9)
    prof = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name='prof',default=3)
    professeurs = models.ManyToManyField(User, blank=False, null=False, related_name='professeurs',default=1)
    
    def __str__(self):
        return self.name
    
class Oral(models.Model):
    eleve = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    exercices = models.ManyToManyField(Exercice)
    note = models.PositiveIntegerField()
    commentaire = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published',default=timezone.now)
    
    def __str__(self):
        return 'oral '+str(self.id)
    
class Colle(models.Model):
    oraux = models.ManyToManyField(Oral)
    author = models.ForeignKey(User,default=3)
    pub_date = models.DateTimeField('date published',default=timezone.now)
    
    def __str__(self):
        return 'colle '+str(self.id)
    
    