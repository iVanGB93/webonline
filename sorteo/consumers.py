from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
import random
from django.utils import timezone
from django.core.mail import send_mail

from .models import Sorteo, SorteoDetalle
from servicios.models import Recarga


class SorteoWSConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )        
        self.accept()

    def receive(self, text_data):
        data = json.loads(text_data)
        accion = data['accion']
        data = data['data']
        self.acciones[accion](self, data)
    
    def saludo(self, data):
        respuesta = {'estado': False, 'finalizado': False}
        celula = data['identidad']
        print(f'{ celula } se ha conectado')
        respuesta['estado'] = True
        respuesta['mensaje'] = f'Bienvenido {celula}, está conectado!!!'
        self.responder(respuesta)

    def empezar(self, data):
        respuesta = {'estado': True, 'finalizado': False}
        mesActual = timezone.now().month
        if SorteoDetalle.objects.filter(mes=mesActual).exists():
            sorteo = SorteoDetalle.objects.get(mes=mesActual)
        else:
            sorteo = SorteoDetalle(mes=mesActual)
        if sorteo.activo:
            respuesta['mensaje'] = 'Ya estaba activo el sorteo.'
            self.responder(respuesta)
        else:
            sorteo.activo = True
            sorteo.save()
            respuesta['mensaje'] = 'Comienza el sorteo!!!'
            self.responder(respuesta)

    def participantes(self, data):
        respuesta = {'estado': True, 'finalizado': False}
        mesActual = timezone.now().month
        if Sorteo.objects.filter(mes=mesActual).exists():
            participants = Sorteo.objects.filter(mes=mesActual)
            respuesta['mensaje'] = 'participantes'
            respuesta['participantes'] = self.participants_to_json(participants)        
        else:
            respuesta['mensaje'] = 'Ningún participante registrado aún!!!'
        if data.get('individual'):
            self.responder(respuesta)
        else:
            self.responder_grupo(respuesta)
    
    def participants_to_json(self, participants):
        result = []
        for participant in participants:
            result.append(self.participant_to_json(participant))
        return result
    
    def participant_to_json(self, participant):
        result = []
        return {
            'id': participant.id,
            'usuario': participant.usuario.username,
            'code': participant.code,
            'eliminado': participant.eliminado,
            'servicio': participant.servicio
        }
        return result

    def sortear(self, data):
        respuesta = {'estado': False, 'finalizado': False}
        mesActual = timezone.now().month
        if SorteoDetalle.objects.filter(mes=mesActual).exists():
            sorteo = SorteoDetalle.objects.get(mes=mesActual)
            participants = Sorteo.objects.filter(eliminado=False, mes=mesActual)
            codes = []
            for p in participants:
                codes.append(p.code)
            if len(codes) > 1:
                if len(codes) == 2:
                    code = random.choice(codes)
                    selected = Sorteo.objects.get(code=code)
                    selected.eliminado = True
                    selected.save()
                    codes.remove(code)                
                    ganador = Sorteo.objects.get(code=codes[0])
                    respuesta['estado'] = True
                    respuesta['mensaje'] = f'El ganador es { ganador.usuario.username }, por el servicios { ganador.servicio }. Felicidades!!!'
                    respuesta['finalizado'] = True
                    recarga = Recarga(cantidad=200)
                    recarga.save()
                    sorteo.ganador = ganador.usuario.username
                    sorteo.recarga = recarga.code
                    sorteo.finalizado = True
                    sorteo.activo = False
                    sorteo.save()          
                    send_mail('FELICIDADES desde QbaRed', f'Usted ha sido el ganador del sorteo del mes {sorteo.mes}, este es su código de recarga {sorteo.recarga}. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [ganador.usuario.email,])
                    self.responder_grupo(respuesta)                    
                else:
                    code = random.choice(codes)
                    selected = Sorteo.objects.get(code=code)
                    selected.eliminado = True
                    selected.save()
                    respuesta['estado'] = True
                    respuesta['mensaje'] = f'El eliminado es {selected.usuario.username}, por el servicio: {selected.servicio}  :-('
                    self.responder_grupo(respuesta)
            else:
                respuesta['estado'] = True
                sorteo.finalizado = True
                sorteo.activo = False
                sorteo.save()
                ganador = sorteo.ganador
                respuesta['mensaje'] = f'Ya ha terminado el sorteo, ganador { ganador }.'
                self.responder_grupo(respuesta)
        else:
            respuesta['estado'] = True
            respuesta['mensaje'] = 'Por favor empiece el sorteo primero'
            self.responder(respuesta)

    acciones = {
        'saludo': saludo,
        'empezar': empezar,
        'participantes': participantes,
        'sortear': sortear,
    }

    def send_message(self, message):
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
    
    # Receive message from room group
    def chat_message(self, event):
        message = event['message']        
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

    def responder(self, data):
        data = json.dumps(data)
        self.send(data)
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )