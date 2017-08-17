from django import forms
from django.contrib.auth.models import User
from .models import Exercice, Folder
from django.contrib.auth.forms import AuthenticationForm 

class ExoForm(forms.ModelForm):
    
    class Meta:
        model = Exercice
        fields = ['enonce_text','corrige_text','tags']
        labels = {
                  'enonce_text': 'énoncé',
                  'corrige_text': 'corrigé',
                  'tags': 'tags',
        }

class ExoSearch(forms.Form):
    my_num = forms.IntegerField(label='numéro d\'exercice', widget=forms.NumberInput(attrs={'style': 'width:15ch' }) )

class ExoSearch2(forms.Form):
    my_tag = forms.CharField(label='tag d\'exercice')
    
class FolderForm(forms.ModelForm):
    
    class Meta:
        model = Folder
        fields = ['name']
        labels = {'name': 'nom',
                  }
    
class FolderAddExercice(forms.Form):
    my_exercices = forms.CharField(label='numéro d\'exercices',help_text='entrer un numéro ou une liste de numéros séparés par une virgule')

    def clean_my_exercices(self):
        data = self.cleaned_data['my_exercices']    
        data = data.replace(';',',').replace(' ',',').split(',')
        data = [int(x) for x in data]   
        return data

class ExerciceAddToFolder(forms.Form):
    my_folder = forms.IntegerField(label='numéro de dossier')

class FolderForm2(forms.Form):
    name = forms.CharField(max_length=20)
    exercices = forms.ModelMultipleChoiceField(queryset=Exercice.objects.all())
    
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
    