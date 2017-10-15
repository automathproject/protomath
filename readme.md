#Automath

## Dépendances

Il nécessaire d'avoir django 1.9. minimum

## Installation

1. Récupérer les sources (git ou zip)
2. Installer 'taggit', 'pypandoc' :
  pip install django-taggit
  pip install pypandoc
  
3. Depuis la racine des sources, construire la base de données en tapant
  python manage.py migrate

## Lancement

1: Depuis la racine /src/ taper
  python manage.py runserver
2. Visiter http://localhost:8000/exobase