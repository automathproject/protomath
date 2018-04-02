from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic.list import ListView
#from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission, Group, User
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.contrib import messages
import operator
import pypandoc
from functools import reduce
#from django.core.urlresolvers import reverse
from exobase.models import Exercice, Folder, OrderFolder, Solution, Profile, Classe,\
    MacroLatex
from exobase.forms import ExoForm, ExoSearch, ExoSearch2, NewUser, FolderForm, FolderAddExercice, ExerciceAddSolution, ProfileForm,\
    NewUser2, ClassForm, ClassAddEleve, MacroForm, ClassAddFolder, ExoLatexForm

from taggit.models import Tag 
from django.contrib.contenttypes.models import ContentType

def index(request):
    if request.user.is_authenticated():
        if request.user.profile.work == '':
            messages.add_message(request, messages.WARNING, u'Veuillez renseigner votre statut dans votre profil pour avoir des droits de lecture')
    latest_exercice_list = Exercice.objects.order_by('-pub_date')[:10]
    latest_folder_list = Folder.objects.order_by('-pub_date')[:10]
    context = {'latest_exercice_list': latest_exercice_list, 'latest_folder_list': latest_folder_list}
    return render(request, 'exobase/index.html', context)


def profile_edit(request):
    user = request.user
    profile = get_object_or_404(Profile,pk=user.pk)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        form2 = NewUser2(request.POST, instance = user)
        if form.is_valid():
            profile = form.save(commit=False)
            group_name = 'PUBLIC'
            group =  Group.objects.get(name=group_name)
            user.groups.add(group)
            profile.save()
            form.save_m2m()
            test1 = True
        if form2.is_valid():
            user = form2.save(commit=False)
            user.save()
            form2.save_m2m()
            test2 = True
        if test1 == True or test2 == True:
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
        form2 = NewUser2(instance = user)
    return render(request, 'exobase/profile_edit.html', {'form': form, 'form2': form2, 'profile': profile})

def profile(request):
    user = request.user
    profile = get_object_or_404(Profile, pk=user.pk)
    folder_list = user.folder_set.values('id','name','pub_date')
    PROFS = Group.objects.get(name='PROFS')
    if PROFS in user.groups.all():
        classe_list = Classe.objects.filter(professeurs=user).values('id','name')
    else:
        classe_list = Classe.objects.filter(eleves=user).values('id','name')
    latest_exercices = user.exercice_set.order_by('-pub_date')[:10]
    return render(request, 'exobase/profile.html', {'profile': profile, 'folder_list': folder_list, 'latest_exercices': latest_exercices, 'classe_list': classe_list, })

def detail(request, exercice_id):
    exercice = get_object_or_404(Exercice, pk=exercice_id)
    perm_codename = 'see_exercice_{0}'.format(exercice_id)
    perm =  get_object_or_404(Permission,codename=perm_codename)
    reader_list = User.objects.filter(user_permissions=perm).values_list('username',flat=True)
    group_list = Group.objects.filter(permissions=perm).values_list('name',flat=True)
    classe_list = Classe.objects.filter(name__in=group_list).values_list('id','name')
    return render(request, 'exobase/detail.html', {'exercice': exercice, 'reader_list': reader_list, 'classe_list': classe_list, })

#moteur de recherche en haut de page
class ExerciceList(ListView):
    template_name = 'exobase/exercice_list2.html'
    model = Exercice
    paginate_by = 100

    def get_queryset(self):
        p = Exercice.objects.all()
        query_list = self.request.GET.get('search_box')
        if query_list is not None:
            query_list = query_list.replace(';',',').replace(' ',',').split(',')
            p = p.filter( reduce(operator.and_,((Q(enonce_html__icontains=q) |Q(description__icontains=q) |Q(tags__slug__icontains=slugify(q))  for q in query_list))))
            p=p.distinct()
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
def exercice_tag_list(request, tag_slug=None):
    exercice_list = Exercice.objects.all()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        exercice_list = exercice_list.filter(tags__name__in=[tag])
    context = {'exercice_list': exercice_list, 'tag': tag}
    return render(request, 'exobase/exercice_list2.html', context)

@permission_required('exobase.add_exercice')
def ex_new(request):
    if request.method == "POST":
        form = ExoForm(request.POST)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            user = request.user
            PROFS = Group.objects.get(name='PROFS')
            exercice.author = user
            if exercice.enonce_latex:
                exercice.enonce_html = pypandoc.convert(exercice.enonce_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])
            if exercice.indication_latex:
                exercice.indication_html = pypandoc.convert(exercice.indication_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])
            exercice.save()
            form.save_m2m()
            exercice_id = exercice.id
            content_type = ContentType.objects.get(app_label='exobase', model = 'exercice')
            permission = Permission.objects.create(
                                    codename='see_exercice_{0}'.format(exercice_id),
                                    name='Voir l\'exercice {0}'.format(exercice_id),
                                    content_type = content_type
                                                   )
            user.user_permissions.add(permission)
            PROFS.permissions.add(permission)
            permission = Permission.objects.create(
                                    codename='edit_exercice_{0}'.format(exercice_id),
                                    name='Editer l\'exercice {0}'.format(exercice_id),
                                    content_type = content_type
                                                   )            
            user.user_permissions.add(permission)
            group_name = 'PUBLIC'
            group =  Group.objects.get(name=group_name)
            perm_codename = 'see_exercice_{0}'.format(exercice_id)
            perm =  get_object_or_404(Permission,codename=perm_codename)
            if exercice.get_visibility_display() == 'Public':
                group.permissions.add(perm)
            profs = Group.objects.get(name='PROFS')
            profs.permissions.add(perm)
            return redirect('detail',exercice_id=exercice_id)
    else:
        form = ExoForm()
    return render(request, 'exobase/exercice_edit.html', {'form': form})

@permission_required('exobase.change_exercice')
def ex_edit(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk)
    if request.method == "POST":
        form = ExoForm(request.POST, instance=exercice)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            if exercice.enonce_latex:
                exercice.enonce_html = pypandoc.convert(exercice.enonce_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])
            if exercice.indication_latex:
                exercice.indication_html = pypandoc.convert(exercice.indication_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])  
            exercice.save()
            form.save_m2m()
            group_name = 'PUBLIC'
            group =  Group.objects.get(name=group_name)
            perm_codename = 'see_exercice_{0}'.format(pk)
            perm =  get_object_or_404(Permission,codename=perm_codename)
            if exercice.get_visibility_display() == 'Public':
                group.permissions.add(perm)
            elif perm in group.permissions.all():
                group.permissions.remove(perm)
                
            return redirect('detail', exercice_id=pk)
    else:
        form = ExoForm(instance=exercice)
    return render(request, 'exobase/exercice_edit.html', {'form': form, 'exercice': exercice})   

@permission_required('exobase.change_exercice')
def ex_enonce_edit(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk)
    if request.method == "POST":
        form = ExoLatexForm(request.POST, instance=exercice)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.pub_date = timezone.now()
            if exercice.enonce_latex:
                exercice.enonce_html = pypandoc.convert(exercice.enonce_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])
            exercice.save()
            form.save_m2m()
            return redirect('detail', exercice_id=pk)
    else:
        form = ExoLatexForm(instance=exercice)
    return render(request, 'exobase/exercice_enonce_edit.html', {'form': form, 'exercice': exercice})   

@permission_required('exobase.change_exercice')
def ex_add_perm(request,pk):
    query = request.GET.get('perm_box')
    group_public = Group.objects.get(name='PUBLIC')
    perm_name = 'see_exercice_{0}'.format(pk)
    perm = Permission.objects.get(codename=perm_name)
    if query == 'public':
        group_public.permissions.add(perm)
    else:
        group_public.permissions.remove(perm)
    return redirect('detail',exercice_id=pk)
    
@permission_required('exobase.add_solution')
def exercice_add_solution(request, exercice_id):
    exercice = get_object_or_404(Exercice,pk=exercice_id)
    if request.method == "POST":
        form = ExerciceAddSolution(request.POST)
        if form.is_valid():
            solution = form.save(commit=False)
            solution.enonce_html = pypandoc.convert(solution.enonce_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])
            solution.pub_date = timezone.now()
            user = request.user
            solution.author = user
            solution.exercice = exercice
            solution.save()
            form.save_m2m()
            ctype = ContentType.objects.get(app_label='exobase', model = 'solution')
            permission1 = Permission.objects.create(
                                    codename='see_solution_{0}'.format(solution.id),
                                    name='Voir la solution {0}'.format(solution.id),
                                    content_type = ctype
                                                   )
            user.user_permissions.add(permission1)
            permission2 = Permission.objects.create(
                                    codename='edit_solution_{0}'.format(solution.id),
                                    name='Editer la solution {0}'.format(solution.id),
                                    content_type = ctype
                                                   )            
            user.user_permissions.add(permission2)
            group_name = 'PUBLIC'
            group =  Group.objects.get(name=group_name)
            if solution.get_visibility_display() == 'Public':
                group.permissions.add(permission1)
                
            profs = Group.objects.get(name='PROFS')
            profs.permissions.add(permission1)
            return redirect('detail', exercice_id = exercice.pk)
    else:
        form = ExerciceAddSolution()
    return render(request, 'exobase/exercice_add_solution.html', {'form': form, 'exercice': exercice, 'exercice_id': exercice_id})

@permission_required('exobase.change_solution')
def solution_edit(request, pk):
    solution = get_object_or_404(Solution, pk=pk)
    exercice_id = solution.exercice.id
    exercice = Exercice.objects.get(pk=exercice_id)
    perm_codename = 'see_solution_{0}'.format(pk)
    perm =  get_object_or_404(Permission,codename=perm_codename)
    reader_list = User.objects.filter(user_permissions=perm).values_list('username',flat=True)
    group_list = Group.objects.filter(permissions=perm).values_list('name',flat=True)
    classe_list = Classe.objects.filter(name__in=group_list).values_list('id','name')
    if request.method == "POST":
        form = ExerciceAddSolution(request.POST, instance=solution)
        if form.is_valid():
            solution = form.save(commit=False)
            solution.enonce_html = pypandoc.convert(solution.enonce_latex,'html5',format='latex',extra_args=['--mathjax','--smart'])
            solution.pub_date = timezone.now()
            solution.save()
            form.save_m2m()
            group_name = 'PUBLIC'
            group =  Group.objects.get(name=group_name)
            perm = Permission.objects.get(codename='see_solution_{0}'.format(pk))
            if solution.get_visibility_display() == 'Public':
                group.permissions.add(perm)
            elif perm in group.permissions.all():
                group.permissions.remove(perm)
            return redirect('detail', exercice_id=exercice_id)
    else:
        form = ExerciceAddSolution(instance=solution)
    return render(request, 'exobase/solution_edit.html', {'form': form, 'solution': exercice,'solution_id': pk, 'reader_list': reader_list, 'classe_list': classe_list,})     

@permission_required('exobase.change_solution')
def sol_add_perm(request,pk):
    query = request.GET.get('perm_box')
    group_public = Group.objects.get(name='PUBLIC')
    perm_name = 'see_solution_{0}'.format(pk)
    perm = Permission.objects.get(codename=perm_name)
    if query == 'public':
        group_public.permissions.add(perm)
    else:
        group_public.permissions.remove(perm)
    return redirect('solution_edit',pk=pk)

@permission_required('exobase.change_solution')
def sol_add_reader(request,solution_id):
    if request.method == "POST":
        form = request.POST.get('add_reader_box')    
        if form:
            username = str(form)
            if User.objects.filter(username = username).exists():
                user = get_object_or_404(User,username=username)
                perm_name = 'see_solution_{0}'.format(solution_id)
                perm = Permission.objects.get(codename=perm_name)
                user.user_permissions.add(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Cet utilisateur n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un nom d\'utilisateur')
    return redirect('solution_edit', pk=solution_id)

@permission_required('exobase.change_solution')
def sol_add_group(request,solution_id):
    if request.method == "POST":
        form = request.POST.get('add_group_box')    
        if form:
            try:
                pk = int(form)
            except ValueError:
                messages.add_message(request, messages.WARNING, u'Un nombre entier est attendu')
                return redirect('solution_edit', pk=solution_id)
            if Classe.objects.filter(pk = pk).exists():
                classe = get_object_or_404(Classe,pk = pk)
                group = get_object_or_404(Group,name=classe.name)
                perm_name = 'see_solution_{0}'.format(solution_id)
                perm = Permission.objects.get(codename=perm_name)
                group.permissions.add(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Ce groupe ou cette classe n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro d\'identifiant de classe')
    return redirect('solution_edit', pk=solution_id)

@permission_required('exobase.change_solution')
def sol_delete_reader(request,solution_id):
    if request.method == "POST":
        form = request.POST.get('delete_reader_box')    
        if form:
            username = str(form)
            authorname = Solution.objects.select_related('author').get(pk=solution_id).author.username
            if username == authorname:
                messages.add_message(request, messages.WARNING, u'Vous ne pouvez pas supprimer les droits de lecture de l\'auteur !')
            else:
                if User.objects.filter(username = username).exists():
                    user = get_object_or_404(User,username=username)
                    perm = 'exobase.see_solution_{0}'.format(solution_id)
                    if user.has_perm(perm):
                        user.user_permissions.remove(perm)
                else:
                    messages.add_message(request, messages.WARNING, u'Cet utilisateur n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un nom d\'utilisateur')
    return redirect('solution_edit', pk=solution_id)

@permission_required('exobase.change_solution')
def sol_delete_group(request,solution_id):
    if request.method == "POST":
        form = request.POST.get('delete_group_box')    
        if form:
            try:
                pk = int(form)
            except ValueError:
                messages.add_message(request, messages.WARNING, u'Un nombre entier est attendu')
                return redirect('solution_detail', pk=solution_id)
            if Classe.objects.filter(pk = pk).exists():
                classe = get_object_or_404(Classe,pk = pk)
                group = get_object_or_404(Group,name=classe.name)
                perm_name = 'see_solution_{0}'.format(solution_id)
                perm = Permission.objects.get(codename=perm_name)
                if perm in group.permissions.all():
                    group.permissions.remove(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Ce groupe ou cette classe n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro d\'identifiant de classe')
    return redirect('solution_edit', pk=solution_id)

def solution_detail(request,pk):
    solution = get_object_or_404(Solution, pk=pk)
    return render(request, 'exobase/solution_detail.html', {'solution': solution })

@permission_required('exobase.delete_solution')
def solution_delete(request,pk):
    solution = get_object_or_404(Solution, pk=pk)
    exercice_id = solution.exercice.id
    user = request.user
    perm = 'exobase.edit_solution_{0}'.format(pk)
    if user.has_perm(perm):
        solution.delete()
    else:
        messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé à supprimer cette solution')
    return redirect('detail', exercice_id = exercice_id)     

def macro_new(request):
    if request.method == "POST":
        form = MacroForm(request.POST)
        if form.is_valid():
            macrolatex = form.save(commit=False)
            macrolatex.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = MacroForm()
    return render(request, 'exobase/macro_edit.html', {'form': form,})   

def macro_edit(request,pk):
    macrolatex = get_object_or_404(MacroLatex,pk=pk)
    if request.method == "POST":
        form = MacroForm(request.POST,instance = macrolatex)
        if form.is_valid():
            macrolatex = form.save(commit=False)
            macrolatex.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = MacroForm(instance = macrolatex)
    return render(request, 'exobase/macro_edit.html', {'form': form,})   


@permission_required('exobase.add_folder')
def folder_new(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.pub_date = timezone.now()
            user = request.user
            folder.author = user
            folder.save()
            form.save_m2m()
            content_type = ContentType.objects.get(app_label='exobase', model = 'folder')
            permission = Permission.objects.create(
                                    codename='see_folder_{0}'.format(folder.id),
                                    name='Voir le dossier {0}'.format(folder.id),
                                    content_type = content_type
                                                   )
            user.user_permissions.add(permission)
            permission = Permission.objects.create(
                                    codename='edit_folder_{0}'.format(folder.id),
                                    name='Editer le dossier {0}'.format(folder.id),
                                    content_type = content_type
                                                   )            
            user.user_permissions.add(permission)    
            return redirect('folder_add_exercice',pk=folder.pk)
    else:
        form = FolderForm()
    return render(request, 'exobase/folder_edit.html', {'form': form})

@login_required(redirect_field_name='exobase/login/')
def folder_list(request):
    folder_list = Folder.objects.filter(author=request.user)
    return render(request, 'exobase/folder_list.html', {'folder_list': folder_list,})

@permission_required('exobase.change_folder')
def folder_edit(request, pk):
    user = request.user
    perm = 'exobase.edit_folder_{0}'.format(pk)
    if not user.has_perm(perm):
        messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cet dossier')
        return redirect('folder_detail', folder_id=pk)
    folder = get_object_or_404(Folder, pk=pk)
    if request.method == "POST":
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.pub_date = timezone.now()
            folder.save()
            form.save_m2m()
            return redirect('folder_detail', folder_id=pk)
    else:
        form = FolderForm(instance=folder)
    return render(request, 'exobase/folder_edit.html', {'form': form, 'folder': folder})   


def detail_folder(request, folder_id):
    user = request.user
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
        perm = 'exobase.edit_folder_{0}'.format(folder_id)
        if not user.has_perm(perm):
            messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cet dossier')
            return redirect('folder_detail', folder_id=folder_id)
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
                    messages.add_message(request, messages.WARNING, u'L\'exercice {0} n\'existe pas'.format(str(ex_id)))
            return redirect('folder_detail',folder_id=folder.pk)
    else:
        form = FolderAddExercice()    
    return render(request, 'exobase/detail_folder.html', {'folder': folder , 'order_ex_list': order_ex_list, 'form': form, 'numbermaxplusun': numbermaxplusun})

def resume_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    exercice_in_folder = folder.exercices.all()
    perm_codename = 'see_folder_{0}'.format(folder_id)
    perm =  get_object_or_404(Permission,codename=perm_codename)
    group_list = Group.objects.filter(permissions=perm).values_list('name',flat=True)
    classe_list = Classe.objects.filter(name__in=group_list).values_list('id','name')
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
                        messages.add_message(request, messages.WARNING, u'L\'exercice {0} est déjà dans le dossier'.format(str(ex_id)))
                else:
                    messages.add_message(request, messages.WARNING, u'L\'exercice {0} n\'existe pas'.format(str(ex_id)))
            return redirect('resume_folder',folder_id=folder.pk)
    else:
        form = FolderAddExercice()    
    return render(request, 'exobase/resume_folder.html', {'folder': folder , 'orderfolder_list': orderfolder_list, 'order_ex_list2': order_ex_list, 'form': form, 'numbermaxplusun': numbermaxplusun, 'classe_list': classe_list})



@login_required(redirect_field_name='exobase/login/')
def delete_exercice_folder(request,folder_id,exercice_id):
    user = request.user
    folder = get_object_or_404(Folder, pk=folder_id)
    exercice = get_object_or_404(Exercice, pk=exercice_id)
    orderfolder = get_object_or_404(OrderFolder, folder = folder, exercice = exercice)
    if request.method == "POST":
        perm = 'exobase.edit_folder_{0}'.format(folder_id)
        if not user.has_perm(perm):
            messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cet dossier')
            return redirect('folder_detail', folder_id=folder_id)
        orderfolder.delete()
        orderfolder_list = OrderFolder.objects.filter(folder = folder)
        n=1
        for o in orderfolder_list:
            o.number = n
            o.save()
            n=n+1
    return redirect('folder_detail',folder_id=folder_id)

#inutile car la fonctionnalité existe déjà dans la vue detail_folder
@permission_required('exobase.change_folder')
def folder_add_exercice(request,pk):
    user = request.user
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
            perm = 'exobase.edit_folder_{0}'.format(pk)
            if not user.has_perm(perm):
                messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cet dossier')
                return redirect('folder_detail', folder_id=pk)
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
                    messages.add_message(request, messages.WARNING, u'L\'exercice {0} n\'existe pas.'.format(str(ex_id)))
            return redirect('folder_detail',folder_id=folder.pk)
    else:
        form = FolderAddExercice()
    return render(request, 'exobase/folder_add_exercice.html', {'form': form, 'folder': folder})

@permission_required('exobase.change_folder')
def exercice_add_to_folder(request,exercice_id):
    if request.method == "POST":
        form = request.POST.get('add_ex_box')
        if form:
            folder_id = int(form)
            if Folder.objects.filter(pk=folder_id, author=request.user).exists():
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
                    messages.add_message(request, messages.WARNING, u'Cet exercice est déjà dans le dossier {0}'.format(folder_id))
            else:
                messages.add_message(request, messages.WARNING, u'Le dossier {0} n\'existe pas'.format(folder_id))
                return redirect('detail', exercice_id=exercice_id)
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro de dossier')
            return redirect('detail', exercice_id=exercice_id)
    return redirect('folder_detail',folder_id=folder.pk)

@permission_required('exobase.change_exercice')
def ex_add_reader(request,exercice_id):
    if request.method == "POST":
        form = request.POST.get('add_reader_box')    
        if form:
            username = str(form)
            if User.objects.filter(username = username).exists():
                user = get_object_or_404(User,username=username)
                perm_name = 'see_exercice_{0}'.format(exercice_id)
                perm = Permission.objects.get(codename=perm_name)
                user.user_permissions.add(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Cet utilisateur n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un nom d\'utilisateur')
    return redirect('detail', exercice_id=exercice_id)

@permission_required('exobase.change_exercice')
def ex_add_group(request,exercice_id):
    if request.method == "POST":
        form = request.POST.get('add_group_box')    
        if form:
            try:
                pk = int(form)
            except ValueError:
                messages.add_message(request, messages.WARNING, u'Un nombre entier est attendu')
                return redirect('detail', exercice_id=exercice_id)
            if Classe.objects.filter(pk = pk).exists():
                classe = get_object_or_404(Classe,pk = pk)
                group = get_object_or_404(Group,name=classe.name)
                perm_name = 'see_exercice_{0}'.format(exercice_id)
                perm = Permission.objects.get(codename=perm_name)
                group.permissions.add(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Ce groupe ou cette classe n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro d\'identifiant de classe')
    return redirect('detail', exercice_id=exercice_id)

@permission_required('exobase.change_exercice')
def ex_delete_reader(request,exercice_id):
    if request.method == "POST":
        form = request.POST.get('delete_reader_box')    
        if form:
            username = str(form)
            authorname = Exercice.objects.select_related('author').get(pk=exercice_id).author.username
            if username == authorname:
                messages.add_message(request, messages.WARNING, u'Vous ne pouvez pas supprimer les droits de lecture de l\'auteur !')
            else:
                if User.objects.filter(username = username).exists():
                    user = get_object_or_404(User,username=username)
                    perm = 'exobase.see_exercice_{0}'.format(exercice_id)
                    if user.has_perm(perm):
                        user.user_permissions.remove(perm)
                else:
                    messages.add_message(request, messages.WARNING, u'Cet utilisateur n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un nom d\'utilisateur')
    return redirect('detail', exercice_id=exercice_id)

@permission_required('exobase.change_exercice')
def ex_delete_group(request,exercice_id):
    if request.method == "POST":
        form = request.POST.get('delete_group_box')    
        if form:
            try:
                pk = int(form)
            except ValueError:
                messages.add_message(request, messages.WARNING, u'Un nombre entier est attendu')
                return redirect('detail', exercice_id=exercice_id)
            if Classe.objects.filter(pk = pk).exists():
                classe = get_object_or_404(Classe,pk = pk)
                group = get_object_or_404(Group,name=classe.name)
                perm_name = 'see_exercice_{0}'.format(exercice_id)
                perm = Permission.objects.get(codename=perm_name)
                if perm in group.permissions.all():
                    group.permissions.remove(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Ce groupe ou cette classe n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro d\'identifiant de classe')
    return redirect('detail', exercice_id=exercice_id)

@permission_required('exobase.add_classe')
def classe_new(request):
    if request.method == "POST":
        user = request.user
        perm = 'exobase.add_classe'
        if not user.has_perm(perm):
            messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à créer une classe')
            return redirect('index')
        else:
            form = ClassForm(request.POST)
            if form.is_valid():
                classe = form.save()
                classe.save()
                classe.professeurs.add(user)
                classe_id = classe.id
                classe_name = classe.name
                if not Group.objects.filter(name=classe_name).exists():
                    group = Group.objects.create(name=classe.name)
                    group.save()
                content_type = ContentType.objects.get(app_label='exobase', model = 'classe')
                permission = Permission.objects.create(
                                    codename='see_class_{0}'.format(classe_id),
                                    name='Voir la classe {0}'.format(classe_id),
                                    content_type = content_type
                                                   )
                user.user_permissions.add(permission)
                permission2 = Permission.objects.create(
                                    codename='edit_class_{0}'.format(classe_id),
                                    name='Editer la classe {0}'.format(classe_id),
                                    content_type = content_type
                                                   )
                user.user_permissions.add(permission2)            
                return redirect('classe_detail',pk=classe.pk)
    else:
        form = ClassForm()
    return render(request, 'exobase/classe_edit.html', {'form': form})

@permission_required('exobase.change_classe')
def classe_edit(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == "POST":
        user = request.user
        classe_id = pk
        user = request.user
        perm = 'exobase.edit_class_{0}'.format(classe_id)
        if not user.has_perm(perm):
            messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cette classe')
            return redirect('class_list')
        else:
            form = ClassForm(request.POST, instance=classe)
            if form.is_valid():
                classe = form.save()
                classe.save()
                return redirect('classe_detail',pk=pk)
    else:
        form = ClassForm(instance = classe)
    return render(request, 'exobase/classe_edit.html', {'form': form, 'classe_id': pk})

@permission_required('exobase.delete_classe')
def classe_delete(request,pk):
    classe = get_object_or_404(Classe, pk=pk)
    classe_id = classe.id
    user = request.user
    perm = 'exobase.edit_class_{0}'.format(classe_id)
    if user.has_perm(perm):
        messages.add_message(request, messages.WARNING, u'La classe <<{0}>> a bien été supprimée'.format(classe.name))
        classe.delete()
    else:
        messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé à supprimer cette classe')
    return redirect('index')  


def classe_detail(request,pk):
    classe = Classe.objects.get(pk=pk)
    eleves_in_classe = classe.eleves.all()
    profs_in_classe = classe.professeurs.all()
    try:
        groupe = Group.objects.get(name = classe.name)
        perm_list = groupe.permissions.filter(codename__icontains='see_folder').values_list('codename',flat=True)
        pk_list = [p[11:] for p in perm_list]
    except:
        pk_list = []
        groupe = Group.objects.create(name = classe.name)
    folder_list = Folder.objects.filter(id__in=pk_list)
    if request.method == "POST":
        perm = 'exobase.edit_class_{0}'.format(pk) 
        if request.user.has_perm(perm):
            form = ClassAddEleve(request.POST)
            form2 = ClassAddFolder(request.POST)
        else:
            messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cette classe')
            redirect('classe_detail',pk=pk)
        if form.is_valid():
            my_eleves = form.cleaned_data['my_eleves']
            perm = Permission.objects.get(codename='see_class_{0}'.format(pk))
            for eleve in my_eleves:
                if User.objects.filter(username=eleve).exists():
                    e = User.objects.get(username=eleve)
                    classe.eleves.add(e)
                    e.groups.add(groupe)
                    e.user_permissions.add(perm)
                else:
                    messages.add_message(request, messages.WARNING, u'L\'élève {0} n\'existe pas'.format(eleve))
        if form2.is_valid():
            my_folder = form2.cleaned_data['my_folder']
            if Folder.objects.filter(pk=my_folder).exists():
                perm = Permission.objects.get(codename='see_folder_{0}'.format(str(my_folder)))
                groupe.permissions.add(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Le dossier {0} n\'existe pas'.format(str(my_folder)))
    else:
        form = ClassAddEleve()
        form2 = ClassAddFolder()
    return render(request, 'exobase/class_detail.html', {'form': form, 'form2': form2, 'classe': classe, 'eleves_in_classe': eleves_in_classe, 'profs_in_classe': profs_in_classe, 'folder_list': folder_list})

@permission_required('exobase.change_classe')
def classe_add_folder(request,classe_id):
    if request.method == "POST":
        form = request.POST.get('add_group_box')    
        if form:
            try:
                pk = int(form)
            except ValueError:
                messages.add_message(request, messages.WARNING, u'Un nombre entier est attendu')
                return redirect('classe_detail', pk=classe_id)
            if Folder.objects.filter(pk = pk).exists():
                folder = get_object_or_404(Folder,pk = pk)
                try:
                    classe_name = Classe.objects.get(pk = classe_id).name
                    group = Group.objects.get(name = classe_name)
                except:
                    group = Group.objects.create(name = classe_name)
                perm_name = 'see_folder_{0}'.format(pk)
                perm = Permission.objects.get(codename=perm_name)
                group.permissions.add(perm)
            else:
                messages.add_message(request, messages.WARNING, u'Ce groupe ou cette classe n\'existe pas')
        else:
            messages.add_message(request, messages.WARNING, u'Veuillez entrer un numéro d\'identifiant de classe')
    return redirect('classe_detail', pk=classe_id)


@permission_required('exobase.change_classe')
def delete_eleve_classe(request,classe_id,eleve_id):
    classe = get_object_or_404(Classe,pk=classe_id)
    eleve = get_object_or_404(User,pk=eleve_id)
    perm = 'exobase.edit_class_{0}'.format(classe_id)
    groupe = Group.objects.get(name = classe.name) 
    if request.user.has_perm(perm):
        classe.eleves.remove(eleve)
        eleve.groups.remove(groupe)
        messages.add_message(request, messages.SUCCESS, u'L\'élève {0} a bien été retiré de cette classe'.format(eleve.username))
    else:
        messages.add_message(request, messages.WARNING, u'Vous n\'êtes pas autorisé.e à modifier cette classe')
    return redirect('classe_detail',pk=classe_id)

@login_required(redirect_field_name='exobase/login/')
def classe_list(request):
    user = request.user
    PROFS = Group.objects.get(name='PROFS')
    if PROFS in user.groups.all():
        class_list = Classe.objects.filter(professeurs=user)
    else:
        class_list = Classe.objects.filter(eleves=user)
    return render(request, 'exobase/class_list.html', {'class_list': class_list,})

            
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