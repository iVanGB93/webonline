from channels.generic.websocket import WebsocketConsumer
import json
from django.contrib.auth.models import User
from users.models import Notificacion

class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    
    def disconnect(self, close_code):
        print("CLIENTE DESCONECTADO", close_code)
    
    def saludo(self, data):
        respuesta = {'estado': False}
        celula = data['identidad']
        print(f'{ celula } se ha conectado')
        respuesta['estado'] = True
        respuesta['mensaje'] = f'Bienvenido {celula}, está conectado!!!'
        self.responder(respuesta)
    
    def usuario_existe(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if User.objects.filter(username=usuario).exists():
            return True
        else:
            respuesta['mensaje'] = f'El usuario { usuario } no existe.'
            self.responder(respuesta)
    
    def notificaciones_to_json(self, notificaciones):
        result = []
        for notificacion in notificaciones:
            result.append(self.notificacion_to_json(notificacion))
        return result
    
    def notificacion_to_json(self, notificacion):
        result = []
        return {
            'id': notificacion.id,
            'usuario': notificacion.usuario.username,
            'tipo': notificacion.tipo,
            'vista': notificacion.vista,
            'fecha': str(notificacion.fecha),
            'contenido': notificacion.contenido,
            'sync': notificacion.sync
        }
        return result
    
    def notificaciones(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if self.usuario_existe(data):
            usuario = User.objects.get(username=usuario)
            notificaciones = Notificacion.objects.filter(usuario=usuario).order_by('-fecha')[:30]
            respuesta['notificaciones'] = self.notificaciones_to_json(notificaciones)
            nuevas = Notificacion.objects.filter(usuario=usuario, vista=False)        
            respuesta['nuevas'] = nuevas.count()
            for n in nuevas:
                n.vista = True
                n.save()
            respuesta['accion'] = 'notificaciones'
            respuesta['estado'] = True
            self.responder(respuesta)
    
    def notificaciones_nuevas(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if self.usuario_existe(data):
            usuario = User.objects.get(username=usuario)
            respuesta['nuevas'] = Notificacion.objects.filter(usuario=usuario, vista=False).count()
            respuesta['accion'] = 'nuevas'
            respuesta['estado'] = True
            self.responder(respuesta)

    acciones = {
        'saludo': saludo,
        'notificaciones': notificaciones,
        'notificaciones_nuevas': notificaciones_nuevas,
    }

    def receive(self, text_data):
        data = json.loads(text_data)
        accion = data['accion']
        data = data['data']
        self.acciones[accion](self, data)
    
    def responder(self, data):
        data = json.dumps(data)
        self.send(data)