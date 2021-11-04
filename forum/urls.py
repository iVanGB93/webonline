from django.urls import path
from .views import index, detalles, crear, editar, eliminar

app_name = 'forum'

urlpatterns = [
    path('<str:tema>/', index, name='index'),
    path('<str:tema>/<str:slug>/editar/', editar, name='editar'),
    path('<str:tema>/<str:slug>/eliminar/', eliminar, name='eliminar'),
    path('<str:tema>/<str:slug>/', detalles, name='detalles'),
    path('<str:tema>/crear/nuevo/', crear, name='crear'),
]