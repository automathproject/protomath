from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.utils import timezone
#from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
#from django.core.urlresolvers import reverse
from exobase.models import Exercice
from exobase.forms import ExoForm, ExoSearch, NewUser

def index(request):
    latest_exercice_list = Exercice.objects.order_by('-pub_date')[:10]
    context = {'latest_exercice_list': latest_exercice_list}
    return render(request, 'exobase/index.html', context)


def detail(request, exercice_id):
    exercice = get_object_or_404(Exercice, pk=exercice_id)       
    return render(request, 'exobase/detail.html', {'exercice': exercice, })

@login_required(redirect_field_name='exobase/login/')
def ex_new(request):
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


def recherche(request):
    if request.method == "POST":
        form = ExoSearch(request.POST)
        if form.is_valid():
            my_num = form.cleaned_data['my_num']
            return redirect('detail',exercice_id=my_num)
    else:
        form = ExoSearch()
    return render(request, 'exobase/exercice_search.html', {'form': form})     

def ex_edit(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk)
    if request.method == "POST":
        form = ExoForm(request.POST, instance=exercice)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            exercice.save()
            return redirect('detail', exercice_id=exercice.pk)
    else:
        form = ExoForm(instance=exercice)
    return render(request, 'exobase/exercice_edit.html', {'form': form})   


# 
def user_new(request):
    if request.method == "POST":
        form = NewUser(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = NewUser()
    return render(request, 'exobase/new_user.html',{'form':form})
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/exobase/login")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })