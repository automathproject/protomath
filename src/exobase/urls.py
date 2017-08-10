from django.conf.urls import url
from django.contrib.auth.views import login, logout
from . import views
from .forms import LoginForm


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.exo_list, name='post_list_by_tag'),
    url(r'^taglist/(?P<tag_slug>[-\w]+)$', views.exo_list, name='exo_list'),
    url(r'^list/$', views.ExerciceList.as_view(), name='exo_list2'),
    url(r'^(?P<exercice_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^new/$', views.ex_new, name='post_new'),
    url(r'^search/$', views.recherche, name='recherche'),
    url(r'^search2/$', views.recherche2, name='recherche2'),
    url(r'^post/(?P<pk>[0-9]+)/edit/$', views.ex_edit, name='post_edit'),
    url(r'^newuser/$', views.user_new, name='user_new'),
    url(r'^login/$', login, {'template_name': 'login.html', 'authentication_form': LoginForm}),   
    url(r'^logout/$', logout, {'next_page': '/exobase/login'}),  
    url(r'^register/$', views.register, name='register'),  
]