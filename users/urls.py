from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('logout/', views.salir, name='logout'),
    path('login/', views.entrar, name='login'),
    path('register/', views.register, name='register'),
    path('pullUser/<str:user>/', views.pullUser, name='pullUser'),
]