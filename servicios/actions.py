from django.utils import timezone
from .models import Recarga, Oper, EstadoServicio
from django.contrib.auth.models import User
from users.models import Profile
from sync.syncs import actualizacion_remota
from sync.models import EstadoConexion
from django.core.mail import EmailMessage
from sync.actions import EmailSending
from decouple import config


def comprar_internet(usuario, tipo, contra, duracion, horas, velocidad):
    result = {'correcto': False}
    online = config('APP_MODE')
    if online == 'online':
        conexion = EstadoConexion.objects.get(id=1)
        if not conexion.online:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.internet == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    data = {'usuario': usuario.username, 'servicio': 'internet', 'tipo': tipo, 'contraseña': contra, 'duracion': duracion, 'horas': horas, 'velocidad': velocidad}
    respuesta = actualizacion_remota('comprar_servicio', data=data)
    if tipo == 'horas':
        data['horas'] = horas
    if respuesta['estado']:
        result['correcto'] = True           
    result['mensaje'] = respuesta['mensaje']
    return result

def comprar_jc(usuario):
    result = {'correcto': False}
    online = config('APP_MODE')
    if online == 'online':
        conexion = EstadoConexion.objects.get(id=1)
        if not conexion.online:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    profile = Profile.objects.get(usuario=usuario)
    if profile.coins >= 100:
        data = {'usuario': usuario.username, 'servicio': 'jc'}
        respuesta = actualizacion_remota('comprar_servicio', data=data)
        if respuesta['estado']:
            result['correcto'] = True           
        result['mensaje'] = respuesta['mensaje']
        return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def comprar_emby(usuario):
    result = {'correcto': False}
    online = config('APP_MODE')
    embyPrice = int(config('EMBY_PRICE'))
    if online == 'online':
        conexion = EstadoConexion.objects.get(id=1)
        if not conexion.online:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    profile = Profile.objects.get(usuario=usuario)
    if profile.coins >= embyPrice:
        data = {'usuario': usuario.username, 'servicio': 'emby'}
        respuesta = actualizacion_remota('comprar_servicio', data=data)
        if respuesta['estado']:
            result['correcto'] = True           
        result['mensaje'] = respuesta['mensaje']
        return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def comprar_filezilla(usuario, contraseña):
    result = {'correcto': False}
    online = config('APP_MODE')
    ftpPrice = int(config('FTP_PRICE'))
    if online == 'online':
        conexion = EstadoConexion.objects.get(id=1)
        if not conexion.online:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    profile = Profile.objects.get(usuario=usuario)
    if profile.coins >= ftpPrice:
        data = {'usuario': usuario.username, 'servicio': 'ftp', 'contraseña': contraseña}
        respuesta = actualizacion_remota('comprar_servicio', data=data)
        if respuesta['estado']:
            result['correcto'] = True           
        result['mensaje'] = respuesta['mensaje']
        return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def recargar(code, usuario):
    result = {'correcto': False}
    online = config('APP_MODE')
    if online == 'online':
        conexion = EstadoConexion.objects.get(id=1)
        if not conexion.online:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    usuario = User.objects.get(username=usuario)
    profile = Profile.objects.get(usuario=usuario.id)
    if not profile.sync:
        result['mensaje'] = "Sincronice su perfil en dashboard para poder recargar."
        return result
    if len(code) != 8:
        result['mensaje'] = 'Escriba 8 dígitos.'
        return result
    if Recarga.objects.filter(code=code).exists():
        recarga = Recarga.objects.get(code=code)        
        if recarga.activa:
            cantidad = recarga.cantidad                   
            profile.coins = profile.coins + cantidad
            respuesta = actualizacion_remota('usar_recarga', {'usuario': usuario.username, 'code': code})
            if not respuesta['estado']:
                if respuesta['mensaje'] == 'Esta recarga no existe.':                    
                    email = EmailMessage(f'{ usuario.username } ha recargado desde internet', f'El usuario { usuario.username } recargo su cuenta con { cantidad } coins. Recarga: { code }.', None, ['ivanguachbeltran@gmail.com', 'javymk9026@gmail.com'])    
                    EmailSending(email).start()                   
                else:
                    result['mensaje'] = respuesta['mensaje'] 
                    return result
            profile.sync = False             
            profile.save()
            recarga.activa = False
            recarga.fechaUso = timezone.now()
            recarga.usuario = usuario
            recarga.save()
            oper = Oper(tipo='RECARGA', usuario=usuario, codRec=code, cantidad=cantidad)
            oper.save()
            result['correcto'] = True
            result['mensaje'] = 'Cuenta Recargada con éxito'
            return result
        else:
            result['mensaje'] = 'Recarga usada'
            return result
    else:
        result['mensaje'] = 'Recarga incorrecta'
        return result

def transferir(desde, hacia, cantidad):
    result = {'correcto': False}
    online = config('APP_MODE')
    if online == 'online':
        conexion = EstadoConexion.objects.get(id=1)
        if not conexion.online:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    if User.objects.filter(username=hacia).exists():
        envia = User.objects.get(username=desde)        
        enviaProfile = Profile.objects.get(usuario=envia.id)
        recibe = User.objects.get(username=hacia)
        recibeProfile = Profile.objects.get(usuario=recibe.id)
        if not enviaProfile.sync or not recibeProfile.sync:
            result['mensaje'] = "Sincronice ambos perfiles en dashboard para poder transferir"
            return result  
        coinsDesde = int(enviaProfile.coins) 
        cantidad = int(cantidad)
        if coinsDesde >= cantidad:
            if cantidad >= 20:
                recibeProfile.coins = recibeProfile.coins + cantidad
                enviaProfile.coins = enviaProfile.coins - cantidad 
                enviaProfile.sync = False     
                enviaProfile.save()
                recibeProfile.sync = False
                recibeProfile.save()
                oper = Oper(usuario=recibe, tipo="RECIBO", cantidad=cantidad, haciaDesde=desde)
                oper.save()   
                oper2 = Oper(usuario=envia, tipo="ENVIO", cantidad=cantidad, haciaDesde=hacia)
                oper2.save()      
                result['mensaje']= 'Transferencia realizada con éxito'
                result['correcto'] = True
                return result
            else:
                result['mensaje'] = 'La cantidad mínima es 20'
                return result
        else:
            result['mensaje'] = 'Su cantidad es insuficiente'
            return result
    else:
        result['mensaje'] = 'El usuario de destino no existe'
        return result


