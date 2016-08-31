from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from exobase.models import Exercice
from .forms import ExoForm

def index(request):
    latest_exercice_list = Exercice.objects.order_by('-pub_date')[:10]
    context = {'latest_exercice_list': latest_exercice_list}
    return render(request, 'exobase/index.html', context)

def detail(request, exercice_id):
    exercice = get_object_or_404(Exercice, pk=exercice_id)
    return render(request, 'exobase/detail.html', {'exercice': exercice})

def post_new(request):
    if request.method == "POST":
        form = ExoForm(request.POST)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            exercice.save()
            return redirect('detail',exercice_id=exercice.pk)
    else:
        form = ExoForm()
    return render(request, 'exobase/exercice_edit.html', {'form': form})