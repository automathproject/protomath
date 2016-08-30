from django.shortcuts import render, HttpResponse, get_object_or_404
from exobase.models import Exercice

def index(request):
    latest_exercice_list = Exercice.objects.order_by('-pub_date')[:5]
    context = {'latest_exercice_list': latest_exercice_list}
    return render(request, 'exobase/index.html', context)

def detail(request, exercice_id):
    exercice = get_object_or_404(Exercice, pk=exercice_id)
    return render(request, 'exobase/detail.html', {'exercice': exercice})