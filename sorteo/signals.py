from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sorteo
from sync.syncs import actualizacion_remota
from django.core.mail import send_mail
from decouple import config


@receiver(post_save, sender=Sorteo)
def syncParticipacion(sender, instance, **kwargs):
    online = config('APP_MODE')
    if online == 'online':        
        if instance.sync == False:
            data = {'usuario': instance.usuario.username, 'code': instance.code, 'servicio': instance.servicio}
            respuesta = actualizacion_remota('crear_sorteo', data)
            if respuesta['estado']:
                instance.sync = True
                instance.save()
            else:
                mensaje = respuesta['mensaje']
                send_mail(f'Falló al subir la participacion', f'La participacion del usuario {instance.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])    
