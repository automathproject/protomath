from django.conf.urls import url
from django.contrib.auth.views import login, logout
from . import views
from .forms import LoginForm


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.exo_list, name='post_list_by_tag'),
    url(r'^taglist/(?P<tag_slug>[-\w]+)$', views.exo_list, name='exo_list'),
    url(r'^list/$', views.ExerciceList.as_view(), name='exo_list2'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^exercice/(?P<pk>[0-9]+)/edit/$', views.ex_edit, name='post_edit'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/add/$', views.exercice_add_to_folder, name='exercice_add_to_folder'),
    url(r'^folder/(?P<folder_id>[0-9]+)/$', views.detail_folder, name='detail_folder'),
    url(r'^folder/(?P<pk>[0-9]+)/edit/$', views.folder_edit, name='folder_edit'),
    url(r'^folder/(?P<pk>[0-9]+)/add/$', views.folder_add_exercice, name='folder_add_exercice'),
    url(r'^folder/(?P<folder_id>[0-9]+)/delete/(?P<exercice_id>[0-9]+)/$', views.delete_exercice_folder, name='delete_exercice_folder'),
    url(r'^new/$', views.ex_new, name='post_new'),
    url(r'^new_folder/$', views.folder_new, name='folder_new'),
    url(r'^search/$', views.recherche, name='recherche'),
    url(r'^search2/$', views.recherche2, name='recherche2'),
    url(r'^newuser/$', views.user_new, name='user_new'),
    url(r'^login/$', login, {'template_name': 'login.html', 'authentication_form': LoginForm}),   
    url(r'^logout/$', logout, {'next_page': '/exobase/login'}),  
    url(r'^register/$', views.register, name='register'),  
]