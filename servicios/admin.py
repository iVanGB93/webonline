from django.contrib import admin
from django.forms import TextInput, Textarea, CharField
from django import forms
from .models import Oper, Recarga, EstadoServicio


class EstadosServiciosAdminConfig(admin.ModelAdmin):
    model = EstadoServicio
    search_fields = ['usuario__username']
    list_filter = ('internet', 'emby', 'jc', 'ftp', 'sync')
    ordering = ('usuario',)
    list_display = ('usuario', 'internet', 'emby', 'jc', 'ftp', 'sync')
    fieldsets = (
        (None, {'fields': ('usuario', 'sync')}),
        ('Internet', {'fields': ('internet', 'int_auto', 'int_time', 'int_tipo', 'int_horas')}),
        ('Emby', {'fields': ('emby', 'emby_auto', 'emby_time', 'emby_id')}),  
        ('FileZilla', {'fields': ('ftp', 'ftp_auto', 'ftp_time')}),
        ('Joven Club', {'fields': ('jc', 'jc_auto', 'jc_time')}),      
    )

class OpersAdminConfig(admin.ModelAdmin):
    model = Oper
    search_fields = ['usuario__username', 'code', 'tipo']
    list_filter = ('tipo', 'fecha', 'servicio', 'sync')
    ordering = ('-fecha',)
    list_display = ('usuario', 'tipo', 'servicio', 'cantidad', 'fecha', 'sync')
    fieldsets = (
        ('ID', {'fields': ('code', 'tipo', 'sync')}),
        ('Datos', {'fields': ('usuario', 'servicio', 'cantidad', 'codRec', 'haciaDesde', 'fecha')}),
    )

class RecargasAdminConfig(admin.ModelAdmin):
    model = Recarga
    search_fields = ['usuario__username', 'code']
    list_filter = ('cantidad', 'fechaHecha', 'sync')
    ordering = ('-fechaHecha',)
    list_display = ('code', 'usuario', 'cantidad', 'activa', 'fechaHecha', 'fechaUso', 'sync')
    fieldsets = (
        (None, {'fields': ('code', 'sync', 'usuario', 'cantidad', 'activa', 'fechaHecha', 'fechaUso')}),        
    )


admin.site.register(EstadoServicio, EstadosServiciosAdminConfig)

admin.site.register(Oper, OpersAdminConfig)

admin.site.register(Recarga, RecargasAdminConfig)