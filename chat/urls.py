# chat/urls.py
from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.room, name='index'),
    path('<str:username>/', views.room, name='room'),
]