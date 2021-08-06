from django.contrib import admin
from .models import Sorteo, SorteoDetalle


admin.site.register(SorteoDetalle)

class SorteoAdminConfig(admin.ModelAdmin):
    model = Sorteo
    search_fields = ['usuario__username', 'code', 'mes']
    list_filter = ('eliminado', 'mes', 'servicio', 'fecha')
    ordering = ('-mes',)
    list_display = ('usuario', 'servicio', 'mes', 'eliminado', 'sync', 'fecha')
    fieldsets = (
        ('ID', {'fields': ('usuario', 'code', 'servicio', 'eliminado', 'sync')}),
        ('Fecha', {'fields': ('mes', 'fecha')}),
    )

admin.site.register(Sorteo, SorteoAdminConfig)
