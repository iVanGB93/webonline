from django.db.models.signals import post_save
from django.dispatch import receiver
from servicios.models import Oper, EstadoServicio, Recarga
from django.contrib.auth.models import  User
from servicios.api.serializers import ServiciosSerializer
from sync.syncs import actualizacion_remota
from django.core.mail import send_mail
from decouple import config

@receiver(post_save, sender=User)
def crearServicios(sender, instance, **kwargs):
    usuario = instance.username
    usuario = User.objects.get(username=usuario)
    if EstadoServicio.objects.filter(usuario=usuario).exists():
        pass
    else:        
        servicios = EstadoServicio(usuario=usuario)
        servicios.sync = True
        servicios.save()

@receiver(post_save, sender=EstadoServicio)
def actualizar_servicios(sender, instance, **kwargs):
    if instance.sync == False:
        serializer = ServiciosSerializer(instance)
        data=serializer.data
        data['usuario'] = instance.usuario.username
        respuesta = actualizacion_remota('cambio_servicio', data)
        if respuesta['estado']:
            instance.sync = True
            instance.save()
        else:
            mensaje = respuesta['mensaje']
            send_mail(f'Falló al subir el servicio', f'El servicio del usuario {instance.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])    

@receiver(post_save, sender=Recarga)
def actualizar_recarga(sender, instance, **kwargs):
    if config('APP_MODE') == 'online':
        if instance.sync == False:
            if instance.usuario != None:
                respuesta = actualizacion_remota('usar_recarga', {'usuario': instance.usuario.username, 'code': instance.code})                
                if respuesta['estado'] or respuesta['mensaje'] == 'Esta recarga no existe.':
                    instance.sync = True
                    instance.save()                    
                else:
                    mensaje = respuesta['mensaje']
                    send_mail(f'Falló sync recarga', f'Recarga del usuario {instance.usuario.username} código { instance.code } no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])