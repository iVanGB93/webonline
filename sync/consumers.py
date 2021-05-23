from re import T
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.utils import timezone
from django.core.mail import send_mail

from django.contrib.auth.models import User
from servicios.models import EstadoServicio

class SyncWSConsumer(WebsocketConsumer):
    def connect(self):
        #self.room_name
        self.accept()
        """ usuario = self.scope['user']
        if usuario.is_authenticated:
            print(f"CLIENTE { usuario } CONECTADO")
            
        else:
            print("CONEXION DENEGADA") """
    
    def disconnect(self, close_code):
        print("CLIENTE DESCONECTADO", close_code)
        pass

    def saludo(self, data):
        data = data['data']
        celula = data['identidad']
        print(f'{ celula } se ha conectado')
        command = 'saludo'
        data = {'mensaje': f'bienvenido {celula}, ya esta conectado'}
        envia = {'command': command, 'data': data}
        self.responder(envia)

    def check_usuario(self, data):
        respuesta = {'estado': False}
        if User.objects.filter(username=data['data']['usuario']).exists():
            respuesta['estado'] = True
            self.responder(respuesta)
        else:
            self.responder(respuesta)

    def nuevo_usuario(self, data):
        respuesta = {'estado': False}
        data = data['data']
        usuario = data['usuario']
        email = data['email']
        password = data['password']
        new_user = User(username=usuario, email=email)
        new_user.set_password(password)
        new_user.save()
        respuesta['estado'] = True
        self.responder(respuesta)

    def cambio_usuario(self, data):
        respuesta = {'estado': False}
        data = data['data']
        if User.objects.filter(username=data['usuario']).exists(): 
            usuario_local = User.objects.get(username=data['usuario'])
            usuario_local.email = data['email']
            usuario_local.first_name = data['first_name']
            usuario_local.last_name = data['last_name']
            usuario_local.save()
            respuesta['estado'] = True
            self.responder(respuesta)
        else:
            respuesta['mensaje'] = f'El usuario no existe.'
            self.responder(respuesta)
    
    def check_servicio(self, data):
        respuesta = {'estado': False}
        data = data['data']
        servicio_chequeo = data['servicio']
        if User.objects.filter(username=data['usuario']).exists():
            usuario_local = User.objects.get(username=data['usuario'])
            if EstadoServicio.objects.filter(usuario=usuario_local).exists():
                servicio = EstadoServicio.objects.filter(usuario=usuario_local)
                if servicio_chequeo == 'internet':
                    for s in servicio:
                        if s.internet != data['internet']:
                            self.responder(respuesta)                
                        elif s.int_horas != data['int_horas']:
                            self.responder(respuesta)
                        elif s.int_tipo != data['int_tipo']:
                            self.responder(respuesta)
                        elif s.int_auto != data['int_auto']:
                            self.responder(respuesta)
                        else:
                            respuesta['estado'] = True
                            self.responder(respuesta)
                elif servicio_chequeo == 'jovenclub':
                    for s in servicio:
                        if s.jc != data['jc']:
                            self.responder(respuesta)                
                        elif s.jc_auto != data['jc_auto']:
                            self.responder(respuesta)
                        else:
                            respuesta['estado'] = True
                            self.responder(respuesta)
                elif servicio_chequeo == 'emby':
                    for s in servicio:
                        if s.emby != data['emby']:
                            self.responder(respuesta)                
                        elif s.emby_id != data['emby_id']:
                            self.responder(respuesta)
                        elif s.emby_auto != data['emby_auto']:
                            self.responder(respuesta)
                        else:
                            respuesta['estado'] = True
                            self.responder(respuesta)
                elif servicio_chequeo == 'filezilla':
                    for s in servicio:
                        if s.ftp != data['ftp']:
                            self.responder(respuesta)               
                        elif s.ftp_auto != data['ftp_auto']:
                            self.responder(respuesta)
                        else:
                            respuesta['estado'] = True
                            self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El servicio del usuario no existe.'
                self.responder(respuesta)
        else:
            respuesta['mensaje'] = f'El usuario no existe.'
            self.responder(respuesta)

    def guardar_servicio(self, data):
        respuesta = {'estado': False}
        data = data['data']    
        if User.objects.filter(username=data['usuario']).exists():    
            usuario_local = User.objects.get(username=data['usuario'])
            if EstadoServicio.objects.filter(usuario=usuario_local).exists():
                servicio = EstadoServicio.objects.filter(usuario=usuario_local)
                for s in servicio:
                    s.internet = data['internet']                                  
                    s.int_horas = data['int_horas']
                    s.int_time = data['int_time']
                    s.int_tipo = data['int_tipo']
                    s.int_auto = data['int_auto']                   
                    s.jc = data['jc']
                    s.jc_time = data['jc_time']            
                    s.jc_auto = data['jc_auto']          
                    s.emby = data['emby']             
                    s.emby_id = data['emby_id']
                    s.emby_time = data['emby_time']
                    s.emby_auto != data['emby_auto']
                    s.ftp = data['ftp']              
                    s.ftp_auto = data['ftp_auto']
                    s.ftp_time = data['ftp_time']
                    s.sync = True
                    s.save()
                respuesta['estado'] = True
                self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El servicio del usuario no existe.'
                self.responder(respuesta)
        else:
            respuesta['mensaje'] = f'El usuario no existe.'
            self.responder(respuesta)

    def cambio_servicio(self, data):
        respuesta = {'estado': False}
        data = data['data']
        servicio_cambio = data['servicio']
        if User.objects.filter(username=data['usuario']).exists():
            usuario_local = User.objects.get(username=data['usuario'])
            if EstadoServicio.objects.filter(usuario=usuario_local).exists():
                servicio = EstadoServicio.objects.filter(usuario=usuario_local)
                if servicio_cambio == 'internet':
                    for s in servicio:
                        s.internet = data['internet']                                   
                        s.int_horas = data['int_horas']                  
                        s.int_tipo = data['int_tipo']
                        s.int_time = data['int_time']                   
                        s.int_auto = data['int_auto']
                        s.save()
                    respuesta['estado'] = True
                    self.responder(respuesta)
                elif servicio_cambio == 'jovenclub':
                    for s in servicio:
                        s.jc = data['jc']                                   
                        s.jc_time = data['jc_time']                   
                        s.jc_auto = data['jc_auto']
                        s.save()
                    respuesta['estado'] = True
                    self.responder(respuesta)
                elif servicio_cambio == 'emby':
                    for s in servicio:
                        s.emby = data['emby']                                   
                        s.emby_time = data['emby_time']                   
                        s.emby_id = data['emby_id']                   
                        s.emby_auto = data['emby_auto']
                        s.save()
                    respuesta['estado'] = True
                    self.responder(respuesta)
                elif servicio_cambio == 'filezilla':
                    for s in servicio:
                        s.ftp = data['ftp']                                   
                        s.ftp_time = data['ftp_time']                   
                        s.ftp_auto = data['ftp_auto']
                        s.save()
                    respuesta['estado'] = True
                    self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El servicio del usuario no existe.'
                self.responder(respuesta)
        else:
            respuesta['mensaje'] = f'El usuario no existe.'
            self.responder(respuesta)

    commands = {
        'saludo': saludo,
        'check_usuario': check_usuario,
        'nuevo_usuario': nuevo_usuario,
        'cambio_usuario': cambio_usuario,
        'check_servicio': check_servicio,
        'guardar_servicio': guardar_servicio,
        'cambio_servicio': cambio_servicio,
    }  

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)
    
    def responder(self, data):
        data = json.dumps(data)
        self.send(data)