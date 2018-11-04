from django import template
from django.contrib.auth.models import Group, Permission 
from django.shortcuts import get_object_or_404

register = template.Library()

@register.simple_tag(name='metadata',takes_context=True)
def metadata(context,name_object):
    a=str(name_object.author.username)
    b=name_object.pub_date.strftime("%A %d. %B %Y")
    result = 'Auteur : '+a+' ; Dernière modification : '+b
    return result

@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all() 

@register.filter(name='visible_by_group') 
def visible_by_group(exercice, group_name):
    group =  Group.objects.get(name=group_name)
    perm_codename = 'see_exercice_{0}'.format(exercice.id)
    perm =  get_object_or_404(Permission,codename=perm_codename)
    return perm in group.permissions.all()

@register.filter(name='sol_visible_by_group') 
def sol_visible_by_group(solution, group_name):
    group =  Group.objects.get(name=group_name)
    perm_codename = 'see_solution_{0}'.format(solution.id)
    perm =  get_object_or_404(Permission,codename=perm_codename)
    return perm in group.permissions.all()