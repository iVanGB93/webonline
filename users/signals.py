from sync.syncs import actualizacion_remota
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import  User
from django.core.mail import send_mail
from decouple import config


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
        send_mail('Usuario nuevo', f'El usuario { usuario.username } se ha registardo.', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])
        send_mail(f'Bienvenido { usuario.username } a QbaRed', f'Hola { usuario.username }, usted se ha registrado en QbaRed, le damos todos la bienvenida y esperamos que sea de su agrado nuestra red. Puede informarse en --> https://www.qbared.com/  Saludos', 'RedCentroHabanaCuba@gmail.com', [usuario.email,])

@receiver(post_save, sender=Profile)
def actualizar_profile(sender, instance, **kwargs):
    if config('APP_MODE') == 'online':
        if instance.sync == False:
            data = {'usuario': instance.usuario.username, 'coins': instance.coins}
            respuesta = actualizacion_remota('cambio_perfil', data)
            if respuesta['estado']:
                instance.sync = True
                instance.save()
            else:
                mensaje = respuesta['mensaje']
                send_mail(f'Falló al subir el perfil', f'El perfil del usuario {instance.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])    
