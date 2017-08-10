from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.utils import timezone
from django.views.generic.list import ListView
#from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import operator
from functools import reduce
#from django.core.urlresolvers import reverse
from exobase.models import Exercice
from exobase.forms import ExoForm, ExoSearch, ExoSearch2, NewUser

from taggit.models import Tag 

def index(request):
    latest_exercice_list = Exercice.objects.order_by('-pub_date')[:10]
    context = {'latest_exercice_list': latest_exercice_list}
    return render(request, 'exobase/index.html', context)



def detail(request, exercice_id):
    exercice = get_object_or_404(Exercice, pk=exercice_id)       
    return render(request, 'exobase/detail.html', {'exercice': exercice })

def exo_list(request, tag_slug=None):
    exercice_list = Exercice.objects.all()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        exercice_list = exercice_list.filter(tags__name__in=[tag])
    context = {'exercice_list': exercice_list, 'tag': tag}
    return render(request, 'exobase/exercice_list.html', context)

class ExerciceList(ListView):
    template_name = 'exobase/exercice_list2.html'
    model = Exercice
    paginate_by = 100

    def get_queryset(self):
        p = Exercice.objects.all()
        query_list = self.request.GET.get('search_box')
        if query_list is not None:
            query_list = query_list.split()
            p = p.filter( reduce(operator.and_,(Q(enonce_text__icontains=q) for q in query_list)) |
             reduce(operator.and_,(Q(tags__name__icontains=q) for q in query_list))             )
        return p

@login_required(redirect_field_name='exobase/login/')
def ex_new(request):
    if request.method == "POST":
        form = ExoForm(request.POST)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            exercice.author = request.user
            exercice.save()
            form.save_m2m()
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

def recherche2(request):
    if request.method == "POST":
        form = ExoSearch2(request.POST)
        if form.is_valid():
            my_tag = form.cleaned_data['my_tag']
            return redirect('exo_list',tag_slug = my_tag)
    else:
        form = ExoSearch2()
    return render(request, 'exobase/exercice_search2.html', {'form': form})    
   

@login_required(redirect_field_name='exobase/login/')
def ex_edit(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk)
    if request.method == "POST":
        form = ExoForm(request.POST, instance=exercice)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            exercice.save()
            form.save_m2m()
            return redirect('detail', exercice_id=exercice.pk)
    else:
        form = ExoForm(instance=exercice)
    return render(request, 'exobase/exercice_edit.html', {'form': form, 'exercice': exercice})   


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