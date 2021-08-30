from os import name
from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    path('contra/', views.contra, name='contra'),
    path('internet/', views.internet, name='internet'),
    path('jovenclub/', views.jovenclub, name='jovenclub'),
    path('emby/', views.emby, name='emby'),
    path('filezilla/', views.filezilla, name='filezilla'),
    path('recarga/', views.recarga, name='recarga'),
    path('transferencia/', views.transferencia, name='transferencia'),
    path('operaciones/', views.operaciones, name='operaciones'),
    path('cambiar-auto/<str:id>/', views.cambiar_auto, name="auto"),
    path('sincronizar/<str:id>/', views.sync_servicio, name="sync_servicio"),
    path('guardar-servicio/', views.guardar_servicio, name="guardar_servicio"),
    path('guardar-perfil/', views.guardar_perfil, name="guardar_perfil"),
    path('sync-perfil/', views.sync_perfil, name="sync_perfil"),
]
