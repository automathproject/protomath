from django import forms

from .models import Exercice

class ExoForm(forms.ModelForm):
    
    class Meta:
        model = Exercice
        fields = ('enonce_text','corrige_text')
        labels = {
                  'enonce_text': 'énoncé',
                  'corrige_text': 'corrigé',
        }

class ExoSearch(forms.Form):
    my_num = forms.IntegerField(label='numéro d\'exercice')
    

    