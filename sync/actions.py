from django.contrib.auth.models import User
from servicios.models import EstadoServicio, Oper, Recarga
from users.models import Profile, Notificacion
import threading

from django.core.mail import EmailMessage

from .syncs import actualizacion_remota


class EmailSending(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)

class UpdateThreadServicio(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)
    
    def run(self):
        usuario = User.objects.get(username=self.data['usuario'])
        servicio = EstadoServicio.objects.get(usuario=usuario.id)
        respuesta = actualizacion_remota('cambio_servicio', self.data)
        if respuesta['estado']:
            servicio.sync = True
            servicio.save()
        else:
            mensaje = respuesta['mensaje']
            email = EmailMessage(f'Falló al subir el servicio', f'El servicio del usuario {servicio.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])    
            EmailSending(email).start()

class UpdateThreadOper(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        operacion = Oper.objects.get(code=self.data['code'])
        respuesta = actualizacion_remota('nueva_operacion', self.data)
        if respuesta['estado']:
            operacion.sync = True
            operacion.save()
        else:
            mensaje = respuesta['mensaje']
            email = EmailMessage(f'Falló al subir el servicio', f'La operación de { operacion.tipo } del usuario { operacion.usuario.username }, cantidad { operacion.cantidad }, no se pudo sincronizar con internet, mensaje: { mensaje }. Fecha: { operacion.fecha}.', None, ['ivanguachbeltran@gmail.com'])    
            EmailSending(email).start()

class UpdateThreadPerfil(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        usuario = User.objects.get(username=self.data['usuario'])
        perfil = Profile.objects.get(usuario=usuario.id)
        respuesta = actualizacion_remota('cambio_perfil', self.data)
        if respuesta['estado']:
            perfil.sync = True
            perfil.save()
        else:
            mensaje = respuesta['mensaje']
            email = EmailMessage(f'Falló al subir el perfil desde local_iVan', f'El perfil del usuario {perfil.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])    
            EmailSending(email).start()

class UpdateThreadNotificacion(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)
    
    def run(self):
        notificacion = Notificacion.objects.get(id=self.data['id'])
        respuesta = actualizacion_remota('crear_notificacion', self.data)
        if respuesta['estado']:
            notificacion.sync = True
            notificacion.save()
        else:
            mensaje = respuesta['mensaje']
            email = EmailMessage(f'Falló al subir una notificacion desde local_iVan', f'La notificacion { notificacion.contenido } del usuario {notificacion.usuario.username} no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])    
            EmailSending(email).start()

class UpdateThreadRecarga(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        recarga = Recarga.objects.get(code=self.data['code'])
        if recarga.usuario != None:
            respuesta = actualizacion_remota('usar_recarga', {'usuario': recarga.usuario.username, 'code': recarga.code})
            if respuesta['estado']:
                recarga.sync = True
                recarga.save()
            else:
                mensaje = respuesta['mensaje']
                email = EmailMessage(f'Falló sync recarga usada', f'Recarga del usuario {recarga.usuario.username} código { recarga.code }, que usó no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])
                EmailSending(email).start()
        else:
            respuesta = actualizacion_remota('crear_recarga', self.data)
            if not respuesta['estado']:                 
                mensaje = respuesta['mensaje']
                email = EmailMessage(f'Falló sync recarga', f'Crear recarga, código { recarga.code } no se pudo sincronizar con internet. MENSAJE: { mensaje }', None, ['ivanguachbeltran@gmail.com'])
                EmailSending(email).start()