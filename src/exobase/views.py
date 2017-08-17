from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic.list import ListView
#from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
import operator
from functools import reduce
#from django.core.urlresolvers import reverse
from exobase.models import Exercice, Folder, OrderFolder
from exobase.forms import ExoForm, ExoSearch, ExoSearch2, NewUser, FolderForm, FolderAddExercice

from taggit.models import Tag 

def index(request):
    latest_exercice_list = Exercice.objects.order_by('-pub_date')[:10]
    latest_folder_list = Folder.objects.order_by('-pub_date')[:10]
    context = {'latest_exercice_list': latest_exercice_list, 'latest_folder_list': latest_folder_list}
    return render(request, 'exobase/index.html', context)


def detail(request, exercice_id):
    exercice = get_object_or_404(Exercice, pk=exercice_id) 
    return render(request, 'exobase/detail.html', {'exercice': exercice })




#moteur de recherche en haut de page
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


def recherche(request):
    if request.method == "POST":
        form = ExoSearch(request.POST)
        if form.is_valid():
            my_num = form.cleaned_data['my_num']
            if Exercice.objects.filter(pk=my_num).exists():
                return redirect('detail',exercice_id=my_num)
            else:
                messages.add_message(request, messages.WARNING, u'L\'exercice recherché n\'existe pas')
    else:
        form = ExoSearch()
    return render(request, 'exobase/exercice_search.html', {'form': form})   

def recherche2(request):
    if request.method == "POST":
        form = ExoSearch2(request.POST)
        if form.is_valid():
            my_tag = slugify(form.cleaned_data['my_tag'])
            if Tag.objects.filter(slug = my_tag).exists():
                return redirect('exo_list',tag_slug = my_tag)
            else:
                messages.add_message(request, messages.WARNING, u'Le tag recherché n\'existe pas')
    else:
        form = ExoSearch2()
    return render(request, 'exobase/exercice_search2.html', {'form': form})    

#liste d'exercice après une recherche par tag
def exo_list(request, tag_slug=None):
    exercice_list = Exercice.objects.all()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        exercice_list = exercice_list.filter(tags__name__in=[tag])
    context = {'exercice_list': exercice_list, 'tag': tag}
    return render(request, 'exobase/exercice_list.html', context)

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



@login_required(redirect_field_name='exobase/login/')
def folder_new(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.pub_date = timezone.now()
            folder.author = request.user
            folder.save()
            form.save_m2m()
            return redirect('folder_add_exercice',pk=folder.pk)
    else:
        form = FolderForm()
    return render(request, 'exobase/folder_edit.html', {'form': form})

@login_required(redirect_field_name='exobase/login/')
def folder_edit(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if request.method == "POST":
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.pub_date = timezone.now()
            folder.save()
            form.save_m2m()
            return redirect('detail_folder', folder_id=folder.pk)
    else:
        form = FolderForm(instance=folder)
    return render(request, 'exobase/folder_edit.html', {'form': form, 'folder': folder})   

def detail_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    exercice_in_folder = folder.exercices.all()
    order_ex_list = []
    id_list = []
    for e in exercice_in_folder:
        orderfolder = get_object_or_404(OrderFolder, folder = folder, exercice = e)
        order_ex_list.append([e,orderfolder.number])
        id_list.append(e.pk)        
    orderfolder_list = OrderFolder.objects.filter(folder = folder)
    number_list = []
    for o in orderfolder_list:
        number_list.append(o.number)
    if len(number_list)>0:
        numbermax = max(number_list)
    else:
        numbermax = 0
    numbermaxplusun = numbermax + 1
    if request.method == "POST":
        form = FolderAddExercice(request.POST)
        if form.is_valid():
            my_exercices = form.cleaned_data['my_exercices']
            number=numbermaxplusun
            for ex_id in my_exercices:
                if Exercice.objects.filter(pk = ex_id).exists():
                    exercice = get_object_or_404(Exercice,pk = ex_id)
                    if ex_id not in id_list:
                        o = OrderFolder.objects.create(exercice=exercice,folder=folder,number=number)
                        o.save()
                        number = number +1
                    else:
                        messages.add_message(request, messages.WARNING, u'Cet exercice est déjà dans le dossier')
                else:
                    messages.add_message(request, messages.WARNING, u'L\'exercice n\'existe pas')
            return redirect('detail_folder',folder_id=folder.pk)
    else:
        form = FolderAddExercice()    
    return render(request, 'exobase/detail_folder.html', {'folder': folder , 'order_ex_list': order_ex_list, 'form': form, 'numbermaxplusun': numbermaxplusun})

@login_required(redirect_field_name='exobase/login/')
def delete_exercice_folder(request,folder_id,exercice_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    exercice = get_object_or_404(Exercice, pk=exercice_id)
    orderfolder = get_object_or_404(OrderFolder, folder = folder, exercice = exercice)
    if request.method == "POST":
        orderfolder.delete()
        orderfolder_list = OrderFolder.objects.filter(folder = folder)
        n=1
        for o in orderfolder_list:
            o.number = n
            o.save()
            n=n+1
    return redirect('detail_folder',folder_id=folder_id)

#inutile car la fonctionnalité existe déjà dans la vue detail_folder
@login_required(redirect_field_name='exobase/login/')
def folder_add_exercice(request,pk):
    folder = get_object_or_404(Folder, pk=pk)
    exercice_in_folder = folder.exercices.all()
    id_list = []
    for e in exercice_in_folder:
        id_list.append(e.pk)
    orderfolder_list = OrderFolder.objects.filter(folder = folder)
    number_list = []
    for o in orderfolder_list:
        number_list.append(o.number)
    if len(number_list)>0:
        numbermax = max(number_list)
    else:
        numbermax = 0
    if request.method == "POST":
        form = FolderAddExercice(request.POST)
        if form.is_valid():
            my_exercices = form.cleaned_data['my_exercices']
            number=numbermax+1
            for ex_id in my_exercices:
                if Exercice.objects.filter(pk = ex_id).exists():
                    exercice = Exercice.objects.get(pk = ex_id)
                    if ex_id not in id_list:
                        o = OrderFolder.objects.create(exercice=exercice,folder=folder,number=number)
                        o.save()
                        number = number +1
                    else:
                        messages.add_message(request, messages.WARNING, u'Cet exercice est déjà dans le dossier')
                else:
                    messages.add_message(request, messages.WARNING, u'L\'exercice n\'existe pas')
            return redirect('detail_folder',folder_id=folder.pk)
    else:
        form = FolderAddExercice()
    return render(request, 'exobase/folder_add_exercice.html', {'form': form, 'folder': folder})

@login_required(redirect_field_name='exobase/login/')
def exercice_add_to_folder(request,exercice_id):
    if request.method == "POST":
        form = request.POST.get('add_ex_box')
        if form:
            folder_id = int(form)
            if Folder.objects.filter(pk=folder_id).exists():
                folder = get_object_or_404(Folder,pk=folder_id)
                exercice_in_folder = folder.exercices.all()
                id_list = []
                for e in exercice_in_folder:
                    id_list.append(e.pk)
                orderfolder_list = OrderFolder.objects.filter(folder = folder)
                number_list = []
                for o in orderfolder_list:
                    number_list.append(o.number)
                if len(number_list)>0:
                    numbermax = max(number_list)
                else:
                    numbermax = 0
                number=numbermax+1
                exercice = Exercice.objects.get(pk = exercice_id)
                if exercice not in exercice_in_folder:
                    o = OrderFolder.objects.create(exercice=exercice,folder=folder,number=number)
                    o.save()
                else:
                    messages.add_message(request, messages.WARNING, u'Cet exercice est déjà dans le dossier')
            else:
                messages.add_message(request, messages.WARNING, u'Le dossier n\'existe pas')
                return redirect('detail', exercice_id=exercice_id)
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro de dossier')
            return redirect('detail', exercice_id=exercice_id)
    return redirect('detail_folder',folder_id=folder.pk)
            
            
    





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