from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^price/$', views.fetchPrice, name='fetchPrice'),
    url(r'^order/$', views.orderData, name='orderData'),
    url(r'^heatmap/$', views.heatMap, name='heatMap'),
    url(r'^zone/$', views.getZone, name='getZone'),
    url(r'^shoreline/$', views.getShoreLine, name='getShoreLine'),
    url(r'^upload/$', views.uploadData, name='uploadData'),
    url(r'^point/$', views.pointData, name='pointData'),
]