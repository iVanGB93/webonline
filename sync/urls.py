from django.urls import path
from . import views

app_name = 'sync'

urlpatterns = [
    path('control/', views.control, name='control'),
    path('control/detalles/<str:id>/', views.detalles, name='detalles'),
    path('control/detalles/<str:id>/<str:funcion>/', views.funcion, name='funcion'),
    path('control/usuarios/', views.control_usuarios, name='control_usuarios'),
    path('control/perfiles/', views.control_perfiles, name='control_perfiles'),
    path('control/servicios/', views.control_servicios, name='control_servicios'),
    path('control/usuario/<str:id>/', views.control_usuario, name='control_usuario'),
    path('control/usuario/crear-eliminar-usuario/<str:id>/', views.crear_eliminar_usuario, name='crear_eliminar_usuario'),
    path('control/perfil/<str:id>/', views.control_perfil, name='control_perfil'),
    path('control/perfil/actualizar-perfil/<str:id>/', views.actualizar_perfil, name='actualizar_perfil'),
    path('control/servicio/<str:id>/', views.control_servicio, name='control_servicio'),
    path('control/servicio/actualizar-servicio/<str:id>/', views.actualizar_servicio, name='actualizar_servicio'),
    path('control/recargas/', views.control_recargas, name='control_recargas'),
    path('control/sorteos/', views.control_sorteos, name='control_sorteos'),
    path('control/avanzado/', views.control_avanzado, name='control_avanzado'),
    path('control/finanzas/', views.control_finanzas, name='control_finanzas'),
]
