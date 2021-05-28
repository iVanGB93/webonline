from django.contrib import admin
from .models import Profile, Notificacion

admin.site.register(Notificacion)

class ProfileAdminConfig(admin.ModelAdmin):
    model = Profile
    search_fields = ['usuario__username']
    #list_filter = ('is_active', 'is_staff')
    ordering = ('-coins',)
    list_display = ('usuario', 'id', 'coins', 'sync')
    fieldsets = (
        (None, {'fields': ('usuario', 'coins', 'sync', 'imagen')}),
    )   
    """ add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name', 'email', 'first_name', 'password1', 'password2', 'is_active', 'is_staff')}
         ), """

admin.site.register(Profile, ProfileAdminConfig)
