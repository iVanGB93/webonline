from django.contrib.auth.models import User
from servicios.models import EstadoServicio, Oper, Recarga
from sorteo.models import Sorteo
from users.models import Profile, Notificacion
from users.api.serializers import ProfileSerializer
from sync.models import EstadoConexion
from forum.models import Publicacion
from decouple import config
import threading
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.core.mail import send_mail

from .syncs import actualizacion_remota
from users.actions import create_user


emailAlerts = config('EMAIL_ALERTS', cast=lambda x: x.split(','))

def email_backup(subject, message):
    from_email = 'admin@qbared.com'
    to_email = ['ivanguachbeltran@gmail.com']
    send_mail(subject, message, from_email, to_email, fail_silently=False)

class DynamicEmailSending(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)
    
    def run(self):
        to = self.data['to']
        message = Mail(from_email='QbaRed <admin@qbared.com>', to_emails=to)
        message.template_id = self.data['template_id']
        message.dynamic_template_data = self.data['dynamicdata']
        try:
            api_key = config('EMAIL_API_KEY')
            sg = SendGridAPIClient(api_key)
            sg.send(message)
        except Exception as e:
            data = {'subjet': f'Falló al enviar email dinamico', 'content': f'El email para { to }, de la plantilla { message.template_id } con la data { message.dynamic_template_data } no se pudo enviar. MENSAJE: SALTO EL TRY por { str(e) }', 'to': emailAlerts}    
            EmailSending(data).start()

class EmailSending(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)
    
    def run(self):
        to = self.data['to']
        content = self.data['content']
        subjet = self.data['subjet']
        message = Mail(from_email='QbaRed <admin@qbared.com>', to_emails=to, subject=subjet, html_content=f'<strong>{ content }</strong>')
        try:
            api_key = config('EMAIL_API_KEY')
            sg = SendGridAPIClient(api_key)
            sg.send(message)
        except Exception as e:
            send_mail('Fallo al enviar email', f'Este es el email backup, porque no se pudo enviar el email {content} a {str(to)} EXCEPTION: { str(e)}')

""" class UpdateThreadServicio(threading.Thread):
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
            email = EmailMessage(f'Falló al guardar el servicio', f'El servicio del usuario {servicio.usuario.username} no se pudo sincronizar con la local. MENSAJE: { mensaje }', None, emailAlerts)    
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
            email = EmailMessage(f'Falló al guardar la operación', f'La operación de { operacion.tipo } del usuario { operacion.usuario.username }, cantidad { operacion.cantidad }, no se pudo sincronizar con la local, mensaje: { mensaje }. Fecha: { operacion.fecha}.', None, emailAlerts)    
            EmailSending(email).start() """

class UpdateThreadPerfil(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        usuario = User.objects.get(username=self.data['usuario'])
        perfil = Profile.objects.get(usuario=usuario)
        serializer = ProfileSerializer(perfil)
        data=serializer.data
        conexion = EstadoConexion.objects.get(servidor=perfil.subnet)
        url = f'http://{ conexion.ip_cliente }/api/users/profile/{ usuario.username }/'
        try:
            respuesta = requests.put(url, json=data)
            respuesta = respuesta.json()
            if respuesta['estado']:
                perfil.sync = True
                perfil.save()
            else:
                mensaje = respuesta['mensaje']
                data = {'subject': f'Falló al guardar el perfil { perfil.id }', 'content': f'El perfil del usuario {perfil.usuario.username} no se pudo sincronizar con la local. MENSAJE: { mensaje }', 'to': emailAlerts}   
                EmailSending(data).start()
        except:
            data = {'subject': f'Falló al guardar el perfil { perfil.id }', 'content': f'El perfil del usuario {usuario.username} no se pudo sincronizar con la local. MENSAJE: SALTO EL TRY', 'to': emailAlerts}  
            EmailSending(data).start()

class UpdateThreadNotificacion(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)
    
    def run(self):
        notificacion = Notificacion.objects.get(id=self.data['id'])
        usuario = User.objects.get(username=self.data['usuario'])
        perfil = Profile.objects.get(usuario=usuario)
        conexion = EstadoConexion.objects.get(servidor=perfil.subnet)
        url = f'http://{ conexion.ip_cliente }/api/users/notification/{ usuario.username }/'
        data = self.data
        try:
            respuesta = requests.put(url, json=data)
            respuesta = respuesta.json()
            if respuesta['estado']:
                notificacion.sync = True
                notificacion.save()
            else:
                mensaje = respuesta['mensaje']
                data = {'subject': f'Falló al guardar una notificacion { notificacion.id }', 'content': f'La notificacion { notificacion.contenido } del usuario {notificacion.usuario.username} no se pudo sincronizar con la local. MENSAJE: { mensaje }', 'to': emailAlerts}    
                EmailSending(data).start()
        except:
            data = {'subject': f'Falló al guardar una notificacion { notificacion.id }', 'content': f'La notificacion { notificacion.contenido } del usuario {notificacion.usuario.username} no se pudo sincronizar con la local. MENSAJE: SALTO EL TRY', 'to': emailAlerts}    
            EmailSending(data).start()

""" class UpdateThreadRecarga(threading.Thread):
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
                email = EmailMessage(f'Falló al guardar recarga usada', f'Recarga del usuario {recarga.usuario.username} código { recarga.code }, que usó no se pudo sincronizar con local. MENSAJE: { mensaje }', None, emailAlerts)
                EmailSending(email).start()
        else:
            respuesta = actualizacion_remota('crear_recarga', self.data)
            if not respuesta['estado']:                 
                mensaje = respuesta['mensaje']
                email = EmailMessage(f'Falló al guardar recarga', f'Crear recarga, código { recarga.code } no se pudo sincronizar con local. MENSAJE: { mensaje }', None, emailAlerts)
                EmailSending(email).start() """

class UpdateThreadUsuario(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        usuario = self.data['usuario']
        respuesta =  create_user(usuario, self.data['email'], self.data['password'])
        if not respuesta['state']:
            mensaje = respuesta['message']
            data = {'subject': 'Falló al crear un nuevo usuario', 'content': f'Crear usuario {usuario}, no se pudo sincronizar con local. MENSAJE: { mensaje }', 'to': emailAlerts}
            EmailSending(data).start()

class UpdateThreadSorteo(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        usuario = self.data['usuario']
        participacion = Sorteo.objects.get(id=self.data['id'])
        profile = Profile.objects.get(usuario=usuario)
        self.data['server'] = profile.subnet
        respuesta = actualizacion_remota('crear_sorteo', self.data)
        if respuesta['estado']:
            participacion.sync = True
            participacion.save()
        else:
            mensaje = respuesta['mensaje']
            data = {'subject': f'Falló al guardar la participacion { participacion.id }', 'content': f'La participacion del usuario { usuario } no se pudo sincronizar con local. MENSAJE: { mensaje }', 'to': emailAlerts}    
            EmailSending(data).start()

class UpdateThreadForum(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        usuario = self.data['usuario']
        titulo = self.data['titulo']
        publicacion = Publicacion.objects.get(id=self.data['id'])
        profile = Profile.objects.get(usuario=usuario)
        self.data['server'] = profile.subnet
        respuesta = actualizacion_remota('sync_publicacion', self.data)
        if respuesta['estado']:
            publicacion.sync = True
            publicacion.save()
        else:
            mensaje = respuesta['mensaje']
            data = {'subject': f'Falló al guardar la publicacion { publicacion.id }', 'content': f'La publicacion del usuario { usuario }, titulo: { titulo }, no se pudo sincronizar con local. MENSAJE: { mensaje }', 'to': emailAlerts}    
            EmailSending(data).start()