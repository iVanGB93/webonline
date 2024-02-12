from django.urls import path
from . import views

app_name = 'control'

urlpatterns = [
    path('', views.control, name='control'),
    path('detalles/<str:id>/', views.detalles, name='detalles'),
    path('detalles/<str:id>/<str:funcion>/', views.funcion, name='funcion'),
    path('usuarios/', views.control_usuarios, name='control_usuarios'),
    path('perfiles/', views.control_perfiles, name='control_perfiles'),
    path('servicios/', views.control_servicios, name='control_servicios'),
    path('usuario/<str:id>/', views.control_usuario, name='control_usuario'),
    path('usuario/crear-eliminar-usuario/<str:id>/', views.crear_eliminar_usuario, name='crear_eliminar_usuario'),
    path('perfil/<str:id>/', views.control_perfil, name='control_perfil'),
    path('perfil/actualizar-perfil/<str:id>/', views.actualizar_perfil, name='actualizar_perfil'),
    path('servicio/<str:id>/', views.control_servicio, name='control_servicio'),
    path('servicio/actualizar-servicio/<str:id>/', views.actualizar_servicio, name='actualizar_servicio'),
    path('recargas/', views.control_recargas, name='control_recargas'),
    path('sorteos/', views.control_sorteos, name='control_sorteos'),
    path('avanzado/', views.control_avanzado, name='control_avanzado'),
    path('finanzas/', views.control_finanzas, name='control_finanzas'),
    path('finanzas/<str:id>/', views.finanza_detalles, name='finanza_detalles'),
    path('gasto-nuevo/', views.crear_gasto, name='crear_gasto'),
    path('cerrar-mes/', views.cerrar_mes, name='cerrar_mes'),
    path('ventas/', views.venta_recargas, name='venta_recargas'),
]