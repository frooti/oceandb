from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^login/$', views.login, name='login'),
    #url(r'^logout/$', views.login, name='logout'),
    url(r'^price/$', views.fetchPrice, name='fetchPrice'),
    url(r'^order/$', views.orderData, name='orderData'),
]