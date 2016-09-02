from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<exercice_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^new/$', views.ex_new, name='post_new'),
    url(r'^search/$', views.recherche, name='recherche'),
    url(r'^post/(?P<pk>[0-9]+)/edit/$', views.ex_edit, name='post_edit'),
]