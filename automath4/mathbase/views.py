from django.shortcuts import HttpResponse

def index(request):
    return HttpResponse("Le debut de la base de donnees")