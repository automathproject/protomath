from django import forms
from django.contrib.auth.models import User
from .models import Exercice
from django.contrib.auth.forms import AuthenticationForm 

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
    
class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    
class NewUser(forms.ModelForm):
    class Meta:
        model=User
        fields=('username','password',)
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))
    