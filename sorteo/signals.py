from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sorteo
from sync.actions import UpdateThreadSorteo
from decouple import config


@receiver(post_save, sender=Sorteo)
def syncParticipacion(sender, instance, **kwargs):
    online = config('APP_MODE')
    if online == 'online':
        if instance.sync == False:            
            UpdateThreadSorteo({'id':instance.id, 'usuario': instance.usuario.username, 'code': instance.code, 'servicio': instance.servicio}).start()