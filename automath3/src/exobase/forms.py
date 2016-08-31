from django import forms

from .models import Exercice

class ExoForm(forms.ModelForm):
    
    class Meta:
        model = Exercice
        fields = ('enonce_text','corrige_text')