from django.contrib import admin

# Register your models here.
from .models import Exercice, Folder

admin.site.register(Exercice)
admin.site.register(Folder)
