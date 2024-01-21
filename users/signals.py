from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, Notificacion
from django.contrib.auth.models import  User
from django.core.mail import EmailMessage
from decouple import config

from sync.actions import EmailSending, UpdateThreadPerfil, UpdateThreadNotificacion

@receiver(post_save, sender=User)
def crearProfile(sender, instance, **kwargs):
    usuario = instance.username
    usuario = User.objects.get(username=usuario)
    if Profile.objects.filter(usuario=usuario).exists():
        pass
    else:
        profile = Profile(usuario=usuario)
        profile.sync = True
        profile.save()
        email = EmailMessage('Usuario nuevo', f'El usuario { usuario.username } se ha registrado.', None, ['ivanguachbeltran@gmail.com'])
        EmailSending(email).start()
        email = EmailMessage(f'Bienvenido { usuario.username } a QbaRed', f'Hola { usuario.username }, usted se ha registrado en QbaRed, le damos todos la bienvenida y esperamos que sea de su agrado nuestra red. Puede informarse en --> https://www.qbared.com/  Saludos', None, [usuario.email,])
        EmailSending(email).start()

@receiver(post_save, sender=Profile)
def actualizar_profile(sender, instance, **kwargs):
    if config('APP_MODE') == 'online':
        if instance.sync == False:
            data = {'usuario': instance.usuario.username, 'coins': instance.coins}
            UpdateThreadPerfil(data).start()            

@receiver(post_save, sender=Notificacion)
def actualizar_notificacion(sender, instance, **kwargs):
    if config('APP_MODE') == 'online':
        if instance.sync == False:
            data = {'id': instance.id, 'usuario': instance.usuario.username, 'tipo': instance.tipo, 'contenido': instance.contenido}
            UpdateThreadNotificacion(data).start()