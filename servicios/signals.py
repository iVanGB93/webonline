from django.db.models.signals import post_save
from django.dispatch import receiver
from servicios.models import Oper, EstadoServicio
from django.contrib.auth.models import  User
from servicios.api.serializers import ServiciosSerializer
from sync.syncs import actualizacion_remota
from django.core.mail import send_mail

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

@receiver(post_save, sender=Oper)
def correoOper(sender, instance, **kwargs):
    usuario = str(instance.usuario)
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
    cantidad = instance.cantidad
    fecha = str(instance.fecha)
    data = {'code': instance.code, 'tipo': instance.tipo, 'usuario': usuario, 'servicio': servicio, 'cantidad': instance.cantidad, 'codRec': codRec, 'haciaDesde': haciaDesde, 'fecha': fecha}
    respuesta = actualizacion_remota('nueva_operacion', data)
    if not respuesta['estado']:
        send_mail(f'Falló al subir el servicio', f'La operación de { instance.tipo } del usuario {usuario} no se pudo sincronizar con internet. Fecha: { fecha}.', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])    
    if instance.tipo == 'PAGO':
        send_mail(f'Pago Realizado -- { usuario }', f'El usuario { usuario } pagó { cantidad } por { servicio }. Fecha: { fecha}', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])
    elif instance.tipo == 'RECARGA':
        send_mail(f'{ usuario } ha recargado', f'El usuario { usuario } agregó { cantidad } a su cuenta. Código: { instance.codRec }. Fecha: { fecha}', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])
    elif instance.tipo == 'ENVIO':
        send_mail(f'{ usuario } realizó un envio', f'El usuario { usuario } envió { cantidad } a { instance.haciaDesde }. Fecha: { fecha}', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])
    elif instance == 'RECIBO':
        send_mail(f'{ usuario } ha recibido', f'El usuario { usuario } recibió { cantidad } de { instance.haciaDesde }. Fecha: { fecha}', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])


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
            send_mail(f'Falló al subir el servicio', f'El servicio del usuario {instance.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])    
