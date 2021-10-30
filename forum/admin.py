from django.contrib import admin
from .models import Publicacion, Encuesta, Comentario, RespuestaComentario

class PublicacionAdminConfig(admin.ModelAdmin):
    model = Publicacion
    search_fields = ['autor__username', 'titulo', 'slug']
    list_filter = ('tema', 'sync',)
    ordering = ('-fecha',)
    list_display = ('autor', 'tema', 'visitas', 'titulo', 'sync', 'fecha')
    fieldsets = (
        ('ID', {'fields': ('autor', 'sync', 'visitas')}),
        ('Publicacion', {'fields': ('tema', 'titulo', 'slug', 'contenido')}),
        ('Fecha', {'fields': ('fecha',)}),
        ('Imagenes', {'fields': ('imagen1', 'imagen2', 'imagen3')}),
    )

admin.site.register(Publicacion, PublicacionAdminConfig)


admin.site.register(Encuesta)
admin.site.register(Comentario)
admin.site.register(RespuestaComentario)