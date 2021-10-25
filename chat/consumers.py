import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from django.contrib.auth.models import User
from .models import Chat, Mensaje

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def mensaje_to_json(self, mensaje):
        return {
            'id': mensaje.id,
            'autor': mensaje.autor.username,
            'contenido': mensaje.contenido,
            'fecha': str(mensaje.fecha)
        }
    
    def mensajes_to_json(self, mensajes):
        result = []
        for mensaje in mensajes:
            result.append(self.mensaje_to_json(mensaje))
        return result
    
    def mensajes(self, data):
        respuesta = {'estado': False}
        chat_id = data['id']
        if Chat.objects.filter(id=chat_id).exists():
            chat = Chat.objects.get(id=chat_id)
            mensajes = chat.mensajes.all()            
            respuesta['accion'] = 'mensajes'
            respuesta['mensajes'] = self.mensajes_to_json(mensajes)      
            respuesta['estado'] = True
            self.responder(respuesta)
    
    def mensaje_nuevo(self, data):
        respuesta = {'estado': False}
        chat_id = data['id']
        usuario = User.objects.get(username=data['usuario'])
        contenido = data['mensaje']
        mensaje = Mensaje(autor=usuario, contenido=contenido)
        if Chat.objects.filter(id=chat_id).exists():
            chat = Chat.objects.get(id=chat_id)
            mensaje.save()
            chat.mensajes.add(mensaje)
            respuesta['accion'] = 'mensaje_nuevo'
            respuesta['mensaje'] = self.mensaje_to_json(mensaje)      
            respuesta['estado'] = True
            self.responder_grupo(respuesta)
    
    acciones = {
        'mensajes': mensajes,
        'mensaje_nuevo': mensaje_nuevo,   
    }

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        accion = data['accion']
        data = data['data']
        self.acciones[accion](self, data)

    def responder(self, data):
        data = json.dumps(data)
        self.send(data)
    
    def chat_message(self, event):
        message = event['message']        
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
    
    def responder_grupo(self, data): 
        # Send message to room group  
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data,                
            }
        )