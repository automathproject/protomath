from django.shortcuts import HttpResponse

def index(request):
    return HttpResponse("Kikoo, c'est parti")
