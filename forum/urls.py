from django.urls import path
from .views import index, detalles, crear, editar, eliminar

app_name = 'forum'

urlpatterns = [
    path('<str:pk>/', index, name='index'),
    path('<str:tema>/<int:pk>/editar/', editar, name='editar'),
    path('<str:tema>/<int:pk>/eliminar/', eliminar, name='eliminar'),
    path('<str:tema>/<int:pk>/', detalles, name='detalles'),
    path('<str:tema>/nuevo/', crear, name='crear'),
]