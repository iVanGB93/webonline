from django.db.models.signals import post_save
from django.dispatch import receiver
from servicios.models import EstadoServicio
from users.models import Profile
from sync.models import EstadoConexion
from django.contrib.auth.models import  User
from servicios.api.serializers import ServiciosSerializer
from django.core.mail import EmailMessage
from sync.actions import EmailSending
from decouple import config
import requests

emailAlerts = config('EMAIL_ALERTS', cast=lambda x: x.split(','))

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
        profile = Profile.objects.get(usuario=instance.usuario)
        conexion = EstadoConexion.objects.get(servidor=profile.subnet)
        url = f'http://{ conexion.ip_cliente }/api/servicios/{ instance.usuario.username }/'
        try:
            respuesta = requests.put(url, json=data)
            respuesta = respuesta.json()
            if respuesta['estado']:
                instance.sync = True
                instance.save()
            else:
                mensaje = respuesta['mensaje']
                email = EmailMessage(f'Falló al subir el servicio', f'El servicio del usuario {instance.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, emailAlerts)
                EmailSending(email).start()
        except:
            email = EmailMessage(f'Falló al subir el servicio', f'El servicio del usuario {instance.usuario.username} no se pudo sincronizar con internet. MENSAJE: FALLO EL TRY', None, emailAlerts)
            EmailSending(email).start()