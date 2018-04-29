from django import forms
from django.contrib.auth.models import User
from .models import Exercice, Folder, Profile, Classe
from django.contrib.auth.forms import AuthenticationForm 
from exobase.models import Solution, MacroLatex

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['bio','organization','birth_date','work','website']
        labels = {'work': 'Statut'}

class ExoForm(forms.ModelForm):
    
    class Meta:
        model = Exercice
        fields = ['name',
                  'visibility',
                  'description',
                  'indication_latex',
                  'macro',
                  'tags']
        labels = {
                  'name': 'Nom de l\'exercice',
                  'visibility': 'Visibilité',
                  'description': 'Description',
                  'indication_latex': 'Indications en LaTeX',
                  'macro': 'Sélectionner un fichier de macros LaTeX',
                  'tags': 'tags',
        }

class ExoForm0(forms.ModelForm):
    
    class Meta:
        model = Exercice
        fields = ['name',
                  'visibility',
                  'description',
                  'enonce_latex',
                  'indication_latex',
                  'macro',
                  'tags']
        labels = {
                  'name': 'Nom de l\'exercice',
                  'visibility': 'Visibilité',
                  'description': 'Description',
                  'enonce_latex': 'Enoncé (en LaTeX)',
                  'indication_latex': 'Indications en LaTeX',
                  'macro': 'Sélectionner un fichier de macros LaTeX',
                  'tags': 'tags',
        }

class ExoLatexForm(forms.ModelForm):
    
    class Meta:
        model = Exercice
        fields = ['enonce_latex',
                  ]
        labels = {
                  'enonce_latex': 'Source LaTeX de l\'énoncé',
        }

class ExoSearch(forms.Form):
    my_num = forms.IntegerField(label='numéro d\'exercice', widget=forms.NumberInput(attrs={'style': 'width:15ch' }) )

class ExoSearch2(forms.Form):
    my_tag = forms.CharField(label='tag d\'exercice')

class ExerciceAddSolution(forms.ModelForm):
    
    class Meta:
        model = Solution
        fields = ['enonce_latex','visibility',]
        labels = {'enonce_latex': 'Enoncé en LaTeX','visibility': 'Visibilité',}

class MacroForm(forms.ModelForm):
    
    class Meta:
        model = MacroLatex
        fields = ['name','description','macro']

class FolderForm(forms.ModelForm):
    
    class Meta:
        model = Folder
        fields = ['name','description',]
        labels = {'name': 'Nom du dossier', 'description': 'Description',
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

class ClassForm(forms.ModelForm):
    
    class Meta:
        model = Classe
        fields = ('name','description',)
        
class ClassAddEleve(forms.Form):
    my_eleves = forms.CharField(label='identifiants d\'eleves',help_text='entrer un login ou une liste de login séparés par une virgule')

    def clean_my_eleves(self):
        data = self.cleaned_data['my_eleves']    
        data = data.replace(';',',').replace(' ',',').split(',')
        data = [str(x) for x in data]   
        return data

class ClassAddFolder(forms.Form):
    my_folder = forms.IntegerField(label='numéro de dossier',help_text='entrer un numéro identifiant de dossier')

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    
class NewUser(forms.ModelForm):
    class Meta:
        model=User
        fields=('username','password',)
        
class NewUser2(forms.ModelForm):
    class Meta:
        model=User
        fields=('username','first_name','last_name','email')
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))
    