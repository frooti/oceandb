from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^login/$', views.login, name='login'),
    #url(r'^logout/$', views.login, name='logout'),
    url(r'^fetchPrice/$', views.fetchPrice, name='fetchPrice'),
    url(r'^fetchData/$', views.fetchData, name='fetchData'),
]