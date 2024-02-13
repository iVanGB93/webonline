from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, Notificacion
from django.contrib.auth.models import  User
from decouple import config

from sync.actions import EmailSending, UpdateThreadPerfil, UpdateThreadNotificacion, DynamicEmailSending

emailAlerts = config('EMAIL_ALERTS', cast=lambda x: x.split(','))

@receiver(post_save, sender=User)
def crearProfile(sender, instance, **kwargs):
    usuario = instance.username
    usuario = User.objects.get(username=usuario)
    if not Profile.objects.filter(usuario=usuario).exists():
        profile = Profile(usuario=usuario)
        profile.sync = True
        profile.save()
        if config('NOMBRE_SERVIDOR') == 'core_ONLINE':
            data = {'subjet': 'Usuario nuevo', 'content': f'El usuario { usuario.username } se ha registrado en { profile.subnet }.', 'to': emailAlerts}
            EmailSending(data).start()
            data = {'to': usuario.email, 'template_id': 'd-e48acff5ca9f407b88de9fc53f6c83a8', 'dynamicdata': {'first_name': usuario.username}}
            DynamicEmailSending(data).start()

@receiver(post_save, sender=Profile)
def actualizar_profile(sender, instance, **kwargs):
    if instance.sync == False:
        data = {'usuario': instance.usuario.username, 'coins': instance.coins, 'subnet': instance.subnet}
        UpdateThreadPerfil(data).start()            

@receiver(post_save, sender=Notificacion)
def actualizar_notificacion(sender, instance, **kwargs):
    if instance.sync == False:
        data = {'id': instance.id, 'usuario': instance.usuario.username, 'tipo': instance.tipo, 'contenido': instance.contenido}
        UpdateThreadNotificacion(data).start()