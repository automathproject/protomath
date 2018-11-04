from django.conf.urls import url
from django.contrib.auth.views import logout, LoginView, PasswordChangeView
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/edit/$', views.profile_edit, name='profile_edit'),
    url(r'^profile/auth/edit/$', views.auth_edit, name='auth_edit'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.exercice_tag_list, name='post_list_by_tag'),
    url(r'^taglist/(?P<tag_slug>[-\w]+)$', views.exercice_tag_list, name='exo_list'),
    url(r'^list/$', views.ExerciceList.as_view(), name='exo_list2'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^exercice/(?P<pk>[0-9]+)/edit/$', views.ex_edit, name='post_edit'),
    url(r'^exercice/(?P<pk>[0-9]+)/enonce_edit/$', views.ex_enonce_edit, name='ex_enonce_edit'),
    url(r'^exercice/(?P<pk>[0-9]+)/addperm/$', views.ex_add_perm, name='ex_add_perm'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/addreader/$', views.ex_add_reader, name='ex_add_reader'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/addgroup/$', views.ex_add_group, name='ex_add_group'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/deletereader/$', views.ex_delete_reader, name='ex_delete_reader'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/deletegroup/$', views.ex_delete_group, name='ex_delete_group'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/solution/add/$', views.exercice_add_solution, name='exercice_add_solution'),
    url(r'^solution/(?P<pk>[0-9]+)/edit/$', views.solution_edit, name='solution_edit'),
    url(r'^solution/(?P<pk>[0-9]+)/$', views.solution_detail, name='solution_detail'),
    url(r'^solution/(?P<solution_id>[0-9]+)/addreader/$', views.sol_add_reader, name='sol_add_reader'),
    url(r'^solution/(?P<solution_id>[0-9]+)/addgroup/$', views.sol_add_group, name='sol_add_group'),
    url(r'^solution/(?P<solution_id>[0-9]+)/deletereader/$', views.sol_delete_reader, name='sol_delete_reader'),
    url(r'^solution/(?P<solution_id>[0-9]+)/deletegroup/$', views.sol_delete_group, name='sol_delete_group'),
    url(r'^solution/(?P<pk>[0-9]+)/delete/$', views.solution_delete, name='solution_delete'),
    url(r'^exercice/(?P<exercice_id>[0-9]+)/add/$', views.exercice_add_to_folder, name='exercice_add_to_folder'),
    url(r'^folder/$', views.folder_list, name='folder_list'),
    url(r'^folder/(?P<folder_id>[0-9]+)/$', views.detail_folder, name='folder_detail'),
    url(r'^folder/(?P<folder_id>[0-9]+)/delete/$', views.folder_delete, name='folder_delete'),
    url(r'^folder/resume/(?P<folder_id>[0-9]+)/$', views.resume_folder, name='folder_resume'),
    url(r'^folder/(?P<folder_id>[0-9]+)/up/(?P<exercice_id>[0-9]+)/$', views.folder_up_exercice, name='folder_up_exercice'),
    url(r'^folder/(?P<folder_id>[0-9]+)/down/(?P<exercice_id>[0-9]+)/$', views.folder_down_exercice, name='folder_down_exercice'),    
    url(r'^folder/(?P<pk>[0-9]+)/edit/$', views.folder_edit, name='folder_edit'),
    url(r'^folder/(?P<pk>[0-9]+)/add/$', views.folder_add_exercice, name='folder_add_exercice'),
    url(r'^folder/(?P<folder_id>[0-9]+)/delete/(?P<exercice_id>[0-9]+)/$', views.delete_exercice_folder, name='delete_exercice_folder'),
    url(r'^new/$', views.ex_new, name='post_new'),
    url(r'^folder/new/$', views.folder_new, name='folder_new'),
    url(r'^class/new/$', views.classe_new, name='classe_new'),
    url(r'^class/$', views.classe_list, name='classe_list'),
    url(r'^class/(?P<pk>[0-9]+)/$', views.classe_detail, name='classe_detail'),
    url(r'^class/(?P<pk>[0-9]+)/edit/$', views.classe_edit, name='classe_edit'),
    url(r'^class/(?P<pk>[0-9]+)/addfolder/$', views.classe_add_folder, name='classe_add_folder'),
    url(r'^class/(?P<classe_id>[0-9]+)/delete/$', views.classe_delete, name='classe_delete'),
    url(r'^class/(?P<classe_id>[0-9]+)/(?P<eleve_id>[0-9]+)/delete/$', views.delete_eleve_classe, name='delete_eleve_classe'),
    url(r'^macro/(?P<pk>[0-9]+)/edit/$', views.macro_edit, name='macro_edit'),
    url(r'^macro/new/$', views.macro_new, name='macro_new'),
    url(r'^search/$', views.recherche, name='recherche'),
    url(r'^search2/$', views.recherche2, name='recherche2'),
    url(r'^newuser/$', views.user_new, name='user_new'),
    url(r'^login/$', LoginView.as_view(), name='login'),  
    url(r'^password_change/$', PasswordChangeView.as_view(), name='password_change'),   
    url(r'^logout/$', logout, {'next_page': '/exobase/login'}),  
    url(r'^register/$', views.register, name='register'),  
]