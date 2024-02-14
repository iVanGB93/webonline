from django.db.models.signals import post_save
from django.dispatch import receiver
from servicios.models import EstadoServicio, Oper
from users.models import Profile
from sync.models import EstadoConexion
from django.contrib.auth.models import  User
from servicios.api.serializers import ServiciosSerializer
from sync.actions import EmailSending
from decouple import config
import requests

emailAlerts = config('EMAIL_ALERTS', cast=lambda x: x.split(','))

@receiver(post_save, sender=User)
def crearServicios(sender, instance, **kwargs):
    usuario = instance.username
    usuario = User.objects.get(username=usuario)
    if not EstadoServicio.objects.filter(usuario=usuario).exists():
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
                data = {'subjet': f'Falló al subir el servicio', 'content': f'El servicio del usuario {instance.usuario.username} no se pudo sincronizar con { profile.subnet }. MENSAJE: { mensaje }', 'to': emailAlerts}
                EmailSending(data).start()
        except:
            data = {'subjet': f'Falló al subir el servicio', 'content': f'El servicio del usuario {instance.usuario.username} no se pudo sincronizar con { profile.subnet }. MENSAJE: FALLO EL TRY', 'to': emailAlerts}
            EmailSending(data).start()

@receiver(post_save, sender=Oper)
def actualizar_operacion(sender, instance, **kwargs):
    if instance.sync == False:
        usuario = instance.usuario.username
        if instance.servicio != None:
            servicio = instance.servicio
        else:
            servicio = 'None'
        if instance.codRec != None:
            codRec = instance.codRec
        else:
            codRec = 'None'
        if instance.haciaDesde != None:
            haciaDesde = str(instance.haciaDesde)
        else:
            haciaDesde = 'None'
        fecha = str(instance.fecha)
        profile = Profile.objects.get(usuario=instance.usuario)
        conexion = EstadoConexion.objects.get(servidor=profile.subnet)
        data = {'code': instance.code, 'tipo': instance.tipo, 'usuario': usuario, 'servicio': servicio, 'cantidad': instance.cantidad, 'codRec': codRec, 'haciaDesde': haciaDesde, 'fecha': fecha}
        url = f'http://{ conexion.ip_cliente }/api/servicios/operaciones/{ instance.code }/'
        try:
            response = requests.put(url, data=data)
            if response.status_code == 200:
                instance.sync = True
                instance.save()
                if instance.tipo == 'PAGO':
                    data = {'subjet': f'Pago Realizado -- { usuario } desde internet', 'content': f'El usuario { usuario } de { profile.subnet} pagó { instance.cantidad } por { servicio }. Fecha: { fecha}', 'to': emailAlerts}
                    EmailSending(data).start()
                elif instance.tipo == 'RECARGA':
                    data = {'subjet': f'{ usuario } ha recargado desde internet', 'content': f'El usuario { usuario } de { profile.subnet} agregó { instance.cantidad } a su cuenta. Código: { instance.codRec }. Fecha: { fecha}', 'to': emailAlerts}
                    EmailSending(data).start()
                elif instance.tipo == 'ENVIO':
                    data = {'subjet': f'{ usuario } realizó un envio desde internet', 'content': f'El usuario { usuario } de { profile.subnet} envió { instance.cantidad } a { instance.haciaDesde }. Fecha: { fecha}', 'to': emailAlerts}
                    EmailSending(data).start()
                elif instance == 'RECIBO':
                    data = {'subjet': f'{ usuario } ha recibido desde internet', 'content': f'El usuario { usuario } de { profile.subnet} recibió { instance.cantidad } de { instance.haciaDesde }. Fecha: { fecha}', 'to': emailAlerts}
                    EmailSending(data).start()
            else:
                response = response.json()
                data = {'subjet': f'Error en guardar operacion de { instance.usuario.username } desde internet', 'content': f'La operacion de { instance.usuario.username } no se pudo guardar en el servidor {profile.subnet }. Response { response }', 'to': emailAlerts}    
                EmailSending(data).start()  
        except:
            data = {'subjet': f'Error en guardar operacion de { instance.usuario.username } desde internet', 'content': f'La operacion de { instance.usuario.username } no se pudo guardar en el servidor {profile.subnet }.', 'to': emailAlerts}    
            EmailSending(data).start()