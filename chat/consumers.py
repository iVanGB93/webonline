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
    
    def usuario_to_json(self, usuario):        
        return {
            'id': usuario.id,
            'username': usuario.username,
            'last_login': str(usuario.last_login),
            'img_url': usuario.profile.imagen.url,
        }

    def usuarios_to_json(self, usuarios):
        result = []
        for usuario in usuarios:
            result.append(self.usuario_to_json(usuario))
        return result
    
    def usuarios(self, data):
        respuesta = {'estado': False}
        usuarios = User.objects.all().exclude(username=data['usuario'])
        respuesta['accion'] = 'usuarios'
        respuesta['usuarios'] = self.usuarios_to_json(usuarios)      
        respuesta['estado'] = True
        self.responder(respuesta)

    def mensajes_no_vistos(self, data):
        respuesta = {'estado': False}
        usuario = User.objects.get(username=data['usuario'])
        chats = usuario.chat_set.all()
        if chats:
            for chat in chats:
                cantidad = 0        
                chatID = chat.id                           
                mensajes = chat.mensajes.all()
                for mensaje in mensajes:
                    if mensaje.autor != usuario:
                        cantidad = cantidad + 1
            print(chatID, cantidad)
            respuesta['chatID'] = chatID
            respuesta['accion'] = 'mensajes_no_vistos'
            respuesta['mensajes_no_vistos'] = cantidad
            respuesta['estado'] = True
            self.responder(respuesta)     

    def chats(self, data):
        respuesta = {'estado': False}
        usuario = User.objects.get(username=data['usuario'])
        chats = usuario.chat_set.all()
        if chats:
            chats_list = []
            cantidad = 0        
            for chat in chats:
                contacto = chat.participantes.all().exclude(username=usuario.username)
                contacto = contacto.values('username')[0]
                mensajes = chat.mensajes.all()
                ultimo_mensaje = 'sin mensajes :-('
                if mensajes:
                    contacto_mensajes = chat.mensajes.all().exclude(autor=usuario.id).order_by('-fecha')
                    ultimo_mensaje_try = contacto_mensajes[:1]
                    if ultimo_mensaje_try:
                        ultimo_mensaje = ultimo_mensaje_try[0].contenido
                    mensajes_nuevos = contacto_mensajes.count()               
                new_chat = {'numero': cantidad, 'id': chat.id, 'contacto': contacto['username'], 'ultimo_mensaje': ultimo_mensaje, 'mensajes_nuevos': mensajes_nuevos}
                cantidad = cantidad + 1
                chats_list.append(new_chat)
            respuesta['accion'] = 'chats'
            respuesta['chats_list'] = chats_list
            respuesta['estado'] = True
            self.responder(respuesta)
        else:
            respuesta['mensaje'] = 'ningún chat creado aún'
            self.responder(respuesta)

    acciones = {
        'mensajes': mensajes,
        'mensaje_nuevo': mensaje_nuevo,
        'usuarios': usuarios,
        'mensajes_no_vistos': mensajes_no_vistos,
        'chats': chats,
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