from forum.models import Publicacion
from channels.generic.websocket import WebsocketConsumer
import json
from django.utils import timezone

from django.contrib.auth.models import User
from servicios.models import EstadoServicio, Oper, Recarga
from users.models import Profile, Notificacion
from .models import EstadoConexion
from sorteo.actions import crear_participacion


class SyncWSConsumer(WebsocketConsumer):
    def connect(self):
        #self.room_name
        print("CLIENTE CONECTADO")
        self.accept()
        """ usuario = self.scope['user']
        if usuario.is_authenticated:
            print(f"CLIENTE { usuario } CONECTADO")
            
        else:
            print("CONEXION DENEGADA") """
    
    def disconnect(self, close_code):
        print("CLIENTE DESCONECTADO", close_code)
        pass

    def usuario_existe(self, data):
        respuesta = {'estado': False}
        usuario = data.get('usuario', 'que intenta buscar')
        if User.objects.filter(username=usuario).exists():
            return True
        else:
            respuesta['mensaje'] = f'El usuario { usuario } no existe.'
            self.responder(respuesta)

    def saludo(self, data):
        respuesta = {'estado': False}
        celula = data.get('identidad', 'sin nombre :-(')
        print(f'{ celula } se ha conectado')
        respuesta['estado'] = True
        respuesta['mensaje'] = f'Bienvenido {celula}, está conectado a QbaRed Online!!!'
        self.responder(respuesta)
    
    def chequeo_conexion(self, data):
        respuesta = {'estado': False}
        celula = data['identidad']
        if EstadoConexion.objects.filter(servidor=data['identidad']).exists():
            estado = EstadoConexion.objects.get(servidor=data['identidad'])
            estado.online = True
            estado.fecha_chequeo = timezone.now()
            estado.internet = data['internet']
            estado.jc = data['jc']
            estado.emby = data['emby']
            estado.ftp = data['ftp']
            estado.sync = True
            estado.save()
            respuesta['estado'] = True
            respuesta['mensaje'] = f'Chequeo completado, {celula}!!!'
        else:
            respuesta['mensaje'] = f'Su servidor no esta registrado, {celula}!!!'
        self.responder(respuesta)

    def check_usuario(self, data):
        respuesta = {'estado': False}
        if self.usuario_existe(data):
            respuesta['estado'] = True
            usuario = data['usuario']
            user = User.objects.get(username=usuario)
            respuesta['username'] = user.username
            respuesta['email'] = user.email
            respuesta['mensaje'] = f'El usuario { usuario } esta registrado.'
            self.responder(respuesta)

    def check_email(self, data):
        respuesta = {'estado': False}        
        if User.objects.filter(email=data['email']).exists():
            respuesta['estado'] = True
            respuesta['mensaje'] = f'El correo esta en uso.'
            self.responder(respuesta)
        else:
            self.responder(respuesta)
        
    def nuevo_usuario(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        email = data['email']
        password = data['password']
        new_user = User(username=usuario, email=email)
        new_user.set_password(password)
        new_user.save()
        respuesta['mensaje'] = f'Usuario { usuario } creado con éxito.'
        profile = Profile.objects.get(usuario=new_user)
        profile.subnet = data['subnet']
        profile.save()
        respuesta['estado'] = True
        self.responder(respuesta)

    def cambio_usuario(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if self.usuario_existe(data):
            usuario_local = User.objects.get(username=usuario)
            usuario_local.email = data['email']
            usuario_local.first_name = data['first_name']
            usuario_local.last_name = data['last_name']
            usuario_local.save()
            respuesta['estado'] = True
            respuesta['mensaje'] = f'Usuario { usuario } modificado con éxito.'
            self.responder(respuesta)

    def nueva_contraseña(self, data):
        respuesta = {'estado': False}
        if self.usuario_existe(data):
            usuario = data['usuario']
            usuario_local = User.objects.get(username=usuario)
            nueva = data['contraseña']
            usuario_local.set_password(nueva)
            usuario_local.save()
            respuesta['estado'] = True
            respuesta['mensaje'] = 'Contraseña cambiada con éxito'
            self.responder(respuesta)

    def check_perfil(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if self.usuario_existe(data):
            usuario_local = User.objects.get(username=usuario)
            if Profile.objects.filter(usuario=usuario_local).exists:
                perfil = Profile.objects.filter(usuario=usuario_local)
                for p in perfil:
                    if p.coins != data['coins']:
                        locales = data['coins']
                        respuesta['mensaje'] = f'No coinciden los coins de { usuario }, locales { locales } y remotos { p.coins }'
                        self.responder(respuesta)
                    else:
                        respuesta['mensaje'] = 'Perfiles sincronizados correctamente'
                        respuesta['estado'] = True
                        self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El perfil del usuario { usuario } no existe.'
                self.responder(respuesta)

    def cambio_perfil(self, data):
        respuesta = {'estado': False}
        print(data)
        usuario = data['usuario']
        if self.usuario_existe(data):
            usuario_local = User.objects.get(username=usuario)
            if Profile.objects.filter(usuario=usuario_local).exists:
                perfil = Profile.objects.get(usuario=usuario_local)
                perfil.coins = data['coins']
                perfil.sync = True
                perfil.save()
                respuesta['estado'] = True
                respuesta['mensaje'] = f'Perfil de { usuario } actualizado con éxito'
                self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El perfil de { usuario } no existe.'
                self.responder(respuesta)
    
    def coger_perfil(self, data):
        respuesta = {'estado': False}
        if self.usuario_existe(data):
            usuario = data['usuario']
            usuario_local = User.objects.get(username=usuario)
            if Profile.objects.filter(usuario=usuario_local).exists:
                perfil = Profile.objects.get(usuario=usuario_local)
                respuesta['coins'] = perfil.coins
                respuesta['estado'] = True
                respuesta['mensaje'] = f'Perfil de { usuario } actualizado con éxito'
                self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El perfil del usuario { usuario } no existe.'
                self.responder(respuesta)

    def check_servicio(self, data):
        usuario = data['usuario']
        respuesta = {'estado': False, 'mensaje': f'Los servicios de { usuario } no coinciden'}
        if self.usuario_existe(data):
            usuario_local = User.objects.get(username=usuario)
            if EstadoServicio.objects.filter(usuario=usuario_local).exists():
                servicio = EstadoServicio.objects.filter(usuario=usuario_local)                
                for s in servicio:
                    if s.internet != data['internet']:
                        self.responder(respuesta)                
                    elif s.int_horas != data['int_horas']:
                        self.responder(respuesta)
                    elif s.int_tipo != data['int_tipo']:
                        self.responder(respuesta)
                    elif s.int_duracion != data['int_duracion']:
                        self.responder(respuesta)
                    elif s.int_velocidad != data['int_velocidad']:
                        self.responder(respuesta)
                    elif s.int_auto != data['int_auto']:
                        self.responder(respuesta)
                    elif s.jc != data['jc']:
                        self.responder(respuesta)                
                    elif s.jc_auto != data['jc_auto']:
                        self.responder(respuesta)
                    elif s.emby != data['emby']:
                        self.responder(respuesta)                
                    elif s.emby_id != data['emby_id']:
                        self.responder(respuesta)
                    elif s.emby_auto != data['emby_auto']:
                        self.responder(respuesta)
                    elif s.ftp != data['ftp']:
                        self.responder(respuesta)               
                    elif s.ftp_auto != data['ftp_auto']:
                        self.responder(respuesta)
                    else:
                        s.sync = True
                        s.save()
                        respuesta['estado'] = True
                        respuesta['mensaje'] = f'Servicios de { usuario } sincronizados'
                        self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El servicio del usuario { usuario } no existe.'
                self.responder(respuesta)

    def cambio_servicio(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if self.usuario_existe(data):    
            usuario_local = User.objects.get(username=usuario)
            if EstadoServicio.objects.filter(usuario=usuario_local).exists():
                servicio = EstadoServicio.objects.filter(usuario=usuario_local)
                for s in servicio:
                    s.internet = data['internet']                                  
                    s.int_horas = data['int_horas']
                    s.int_time = data['int_time']
                    s.int_tipo = data['int_tipo']
                    s.int_duracion = data['int_duracion']
                    s.int_velocidad = data['int_velocidad']
                    s.int_auto = data['int_auto']                   
                    s.jc = data['jc']
                    s.jc_time = data['jc_time']            
                    s.jc_auto = data['jc_auto']          
                    s.emby = data['emby']             
                    s.emby_id = data['emby_id']
                    s.emby_time = data['emby_time']
                    s.emby_auto = data['emby_auto']
                    s.ftp = data['ftp']              
                    s.ftp_auto = data['ftp_auto']
                    s.ftp_time = data['ftp_time']
                    s.sync = True
                    s.save()
                respuesta['estado'] = True
                respuesta['mensaje'] = f'Servicio de { usuario } sincronizado con éxito'
                self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El servicio del usuario { usuario } no existe.'
                self.responder(respuesta)
    
    def coger_servicios(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        if self.usuario_existe(data):
            usuario_local = User.objects.get(username=usuario)
            if EstadoServicio.objects.filter(usuario=usuario_local).exists():
                servicio = EstadoServicio.objects.filter(usuario=usuario_local)
                for s in servicio:
                    respuesta['internet'] = s.internet                                 
                    respuesta['int_horas'] = s.int_horas
                    respuesta['int_time'] = str(s.int_time)
                    respuesta['int_tipo'] = s.int_tipo
                    respuesta['int_duracion'] = s.int_duracion
                    respuesta['int_velocidad'] = s.int_velocidad
                    respuesta['int_auto'] = s.int_auto                  
                    respuesta['jc'] = s.jc
                    respuesta['jc_time'] = str(s.jc_time)
                    respuesta['jc_auto'] = s.jc_auto
                    respuesta['emby'] = s.emby            
                    respuesta['emby_id'] = s.emby_id
                    respuesta['emby_time'] = str(s.emby_time)
                    respuesta['emby_auto'] = s.emby_auto
                    respuesta['ftp'] = s.ftp
                    respuesta['ftp_auto'] = s.ftp_auto
                    respuesta['ftp_time'] = str(s.ftp_time)
                    s.sync = True
                    s.save()
                respuesta['estado'] = True
                respuesta['mensaje'] = 'Servicio sincronizado con éxito'
                self.responder(respuesta)
            else:
                respuesta['mensaje'] = f'El servicio del usuario no existe.'
                self.responder(respuesta)
       
    def usar_recarga(self, data):
        respuesta = {'estado': False}
        code = data['code']
        usuario = data['usuario']
        if Recarga.objects.filter(code=code).exists():
            recarga = Recarga.objects.get(code=code)
            if data.get('check') != None:
                respuesta['mensaje'] = 'La recarga existe'
                respuesta['estado'] = True
                respuesta['code'] = recarga.code
                respuesta['cantidad'] = recarga.cantidad
                respuesta['activa'] = recarga.activa
                if recarga.usuario:
                    respuesta['usuario'] = recarga.usuario.username
                respuesta['creator'] = recarga.creator
                respuesta['fecha'] = str(recarga.fechaUso)
                self.responder(respuesta)
            else:
                if recarga.activa:
                    recarga.activa = False
                    usuario = User.objects.get(username=usuario)
                    recarga.usuario = usuario
                    recarga.fechaUso = timezone.now()
                    recarga.sync = True  
                    recarga.save()
                    respuesta['mensaje'] = 'Recarga realizada con éxito'
                    respuesta['estado'] = True
                    self.responder(respuesta)
                else:
                    respuesta['mensaje'] = 'Esta recarga ya fue usada.'
                    self.responder(respuesta)
        else:
            respuesta['mensaje'] = 'Esta recarga no existe.'
            self.responder(respuesta)

    def crear_recarga(self, data):
        respuesta = {'estado': False}
        recarga = Recarga(code=data['code'], cantidad=data['cantidad'], fechaHecha=data['fechaHecha'], creator=data['creator'])
        recarga.sync = True
        recarga.save()
        respuesta['estado'] = True
        self.responder(respuesta)
    
    def nueva_operacion(self, data):
        respuesta = {'estado': False}
        usuario = data['usuario']
        usuario = User.objects.get(username=usuario)
        if data['servicio'] == 'None':
            servicio = None
        else:
            servicio = data['servicio']
        if data['codRec'] == 'None':
            codRec = None
        else:
            codRec = data['codRec']
        if data['haciaDesde'] == 'None':
            haciaDesde = None
        else:
            haciaDesde = data['haciaDesde']
        operacion = Oper(code=data['code'], tipo=data['tipo'], usuario=usuario, servicio=servicio, cantidad=data['cantidad'], codRec=codRec, haciaDesde=haciaDesde, fecha=data['fecha'])
        operacion.sync = True
        operacion.save()
        respuesta['mensaje'] = 'Operación creada con éxito'
        respuesta['estado'] = True
        self.responder(respuesta)
    
    def crear_sorteo(self, data):
        respuesta = {'estado': False}
        usuario = User.objects.get(username=data['usuario'])
        resultado = crear_participacion(usuario, code=data['code'], servicio=data['servicio'], sync=True)
        respuesta['mensaje'] = resultado['mensaje']
        if resultado['estado']:
            respuesta['estado'] = True
        self.responder(respuesta)

    def crear_notificacion(self, data):
        respuesta = {'estado': False}
        usuario = User.objects.get(username=data['usuario'])
        notificacion = Notificacion(usuario=usuario, tipo=data['tipo'], fecha=timezone.now(), contenido=data['contenido'], sync=True)
        notificacion.save()
        respuesta['mensaje'] = 'Notificación guardada con éxito.'
        respuesta['estado'] = True
        self.responder(respuesta)
    
    def sync_publicacion(self, data):
        respuesta = {'estado': False}
        if data.get('check'):
            if data['check']:
                if Publicacion.objects.filter(titulo=data['titulo']).exists():
                    respuesta['estado'] = True
                    respuesta['mensaje'] = 'Existe una publicación con este título.'
                    self.responder(respuesta)
        if self.usuario_existe(data):            
            if Publicacion.objects.filter(titulo=data['titulo']).exists():
                publicacion = Publicacion.objects.get(titulo=data['titulo'])
                publicacion.tema=data['tema']
                publicacion.contenido=data['contenido']
            else:
                autor = User.objects.get(username=data['usuario'])
                publicacion = Publicacion(autor=autor, tema=data['tema'], titulo=data['titulo'], contenido=data['contenido'])
            publicacion.sync = True
            publicacion.save()
            respuesta['mensaje'] = 'Publicación guardada con éxito.'
            respuesta['estado'] = True
            self.responder(respuesta)
    
    def actionError(self, data):
        response = {'estado': False, 'data': 'Nothing to do...'}
        self.responder(response)
    
    def dataError(self, data):
        response = {'estado': False, 'data': 'Nothing to work with...'}
        self.responder(response)
    
    def get_user_info(self, data):
        response = {'estado': False}
        if self.usuario_existe(data):
            user = User.objects.get(username=data['usuario'])
            if not user.check_password(data['password']):
                response['mensaje'] = "Contraseña incorrecta"
                self.responder(response)
            else:
                response['username'] = user.username
                response['email'] = user.email
                profile = Profile.objects.get(usuario=user)
                response['coins'] = profile.coins
                services = EstadoServicio.objects.filter(usuario=user)
                for s in services:
                    response['internet'] = s.internet                                 
                    response['int_horas'] = s.int_horas
                    response['int_time'] = str(s.int_time)
                    response['int_tipo'] = s.int_tipo
                    response['int_duracion'] = s.int_duracion
                    response['int_velocidad'] = s.int_velocidad
                    response['int_auto'] = s.int_auto                  
                    response['jc'] = s.jc
                    response['jc_time'] = str(s.jc_time)
                    response['jc_auto'] = s.jc_auto
                    response['emby'] = s.emby       
                    response['emby_id'] = s.emby_id
                    response['emby_time'] = str(s.emby_time)
                    response['emby_auto'] = s.emby_auto
                    response['ftp'] = s.ftp
                    response['ftp_auto'] = s.ftp_auto
                    response['ftp_time'] = str(s.ftp_time)
                response['estado'] = True
                self.responder(response)

    acciones = {
        'saludo': saludo,
        'chequeo_conexion': chequeo_conexion,
        'check_usuario': check_usuario,
        'check_email': check_email,
        'nuevo_usuario': nuevo_usuario,
        'cambio_usuario': cambio_usuario,
        'nueva_contraseña': nueva_contraseña,
        'check_perfil': check_perfil,
        'cambio_perfil': cambio_perfil,
        'coger_perfil': coger_perfil,
        'check_servicio': check_servicio,
        'cambio_servicio': cambio_servicio,
        'coger_servicios': coger_servicios,
        'usar_recarga': usar_recarga,
        'crear_recarga': crear_recarga,
        'nueva_operacion': nueva_operacion,
        'crear_sorteo': crear_sorteo,
        'crear_notificacion': crear_notificacion,
        'sync_publicacion': sync_publicacion,
        'actionError': actionError,
        'dataError': dataError,
        'get_user_info': get_user_info,
    }  

    def receive(self, text_data):
        if text_data:
            try:
                data = json.loads(text_data)
                if isinstance(data, dict):
                    accion = data.get('accion', 'actionError')
                    data = data.get('data', 'dataError')
                    intentedAction = self.acciones.get(accion, 'notpossible')
                    if intentedAction != 'notpossible':
                        self.acciones[accion](self, data)
                    else:
                        self.responder({'message':'not possible'})
                else:
                    self.responder({'message':'invalid message'})
            except json.JSONDecodeError as e:
                self.responder({'message':'json format error'})
        else:
            self.responder({'message':'empty message'})
    
    def responder(self, data):
        data = json.dumps(data)
        self.send(data)