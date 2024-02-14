from django.utils import timezone
from .models import Recarga, Oper, EstadoServicio
from django.contrib.auth.models import User
from users.models import Profile, Notificacion
from sync.models import EstadoConexion
from sync.actions import EmailSending
from decouple import config
import requests

emailAlerts = config('EMAIL_ALERTS', cast=lambda x: x.split(','))

def comprar_internet(usuario, tipo, contra, duracion, horas, velocidad):
    result = {'correcto': False}
    usuario = User.objects.get(username=usuario)
    profile = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=profile.subnet)
    if not conexion.online:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result
    servicio = EstadoServicio.objects.get(usuario=usuario)
    if servicio.internet == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    url = f'http://{ conexion.ip_cliente }/api/servicios/internet/{ usuario.username }/'
    data = {'usuario': usuario.username, 'tipo': tipo, 'contra': contra, 'duracion': duracion, 'horas': horas, 'velocidad': velocidad}
    try:
        respuesta = requests.put(url, data=data)
        respuesta = respuesta.json()
        if respuesta['estado']:
            result['correcto'] = True
        result['mensaje'] = respuesta['mensaje']
        return result
    except:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result

def comprar_jc(usuario):
    result = {'correcto': False}
    jcPrice = int(config('JC_PRICE'))
    usuario = User.objects.get(username=usuario)
    profile = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=profile.subnet)
    if not conexion.online:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result
    servicio = EstadoServicio.objects.get(usuario=usuario)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    if profile.coins >= jcPrice:
        url = f'http://{ conexion.ip_cliente }/api/servicios/jovenclub/{ usuario.username }/'
        data = {'usuario': usuario.username, 'servicio': 'jc'}
        try:
            respuesta = requests.put(url, data=data)
            respuesta = respuesta.json()
            if respuesta['estado']:
                result['correcto'] = True
            result['mensaje'] = respuesta['mensaje']
            return result
        except:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def comprar_emby(usuario):
    result = {'correcto': False}
    embyPrice = int(config('EMBY_PRICE'))
    usuario = User.objects.get(username=usuario)
    profile = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=profile.subnet)
    if not conexion.online:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    if profile.coins >= embyPrice:
        url = f'http://{ conexion.ip_cliente }/api/servicios/emby/{ usuario.username }/'
        data = {'usuario': usuario.username, 'servicio': 'emby'}
        try:
            respuesta = requests.put(url, data=data)
            respuesta = respuesta.json()
            if respuesta['estado']:
                result['correcto'] = True           
            result['mensaje'] = respuesta['mensaje']
            return result
        except:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def comprar_filezilla(usuario, contraseña):
    result = {'correcto': False}
    ftpPrice = int(config('FTP_PRICE'))
    usuario = User.objects.get(username=usuario)
    profile = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=profile.subnet)
    if not conexion.online:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result
    servicio = EstadoServicio.objects.get(usuario=usuario)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if not servicio.sync:
        result['mensaje'] = 'Debe tener los servicios sincronizados para comprar.'
        return result
    if profile.coins >= ftpPrice:
        url = f'http://{ conexion.ip_cliente }/api/servicios/filezilla/{ usuario.username }/'
        data = {'usuario': usuario.username, 'servicio': 'ftp', 'contraseña': contraseña}
        try:
            respuesta = requests.put(url, data=data)
            respuesta = respuesta.json()
            if respuesta['estado']:
                result['correcto'] = True
            result['mensaje'] = respuesta['mensaje']
            return result
        except:
            result['mensaje'] = "Sistema sin conexión, intente más tarde."
            return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def recargar(code, usuario):
    result = {'correcto': False}
    usuario = User.objects.get(username=usuario)
    profile = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=profile.subnet)
    if not conexion.online:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result
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
            url = f'http://{ conexion.ip_cliente }/api/servicios/recarga/{ code }/'
            data = {'usuario': usuario.username, 'code': code}
            try:
                respuesta = requests.put(url, data=data)
                respuesta = respuesta.json()
                if respuesta.status_code == 200:
                    result['correcto'] = True
                    if not respuesta['estado']:
                        data = {'subjet': f'{ usuario.username } ha recargado desde internet', 'content': f'El usuario { usuario.username } recargo su cuenta con { cantidad } coins. Recarga: { code }.', 'to': emailAlerts}    
                        EmailSending(data).start()
                    profile.sync = False           
                    profile.save()
                    recarga.activa = False
                    recarga.fechaUso = timezone.now()
                    recarga.usuario = usuario
                    recarga.save()
                    oper = Oper(tipo='RECARGA', usuario=usuario, codRec=code, cantidad=cantidad)
                    oper.save()
                    result['mensaje'] = 'Cuenta Recargada con éxito'
                    return result
                else:
                    result['mensaje'] = respuesta
                    return result
            except:
                result['mensaje'] = 'Problemas de conexion con el servidor local, intente mas tarde'
                return result
        else:
            result['mensaje'] = 'Esta recarga ya fue usada'
            return result
    else:
        result['mensaje'] = 'Recarga incorrecta'
        return result

def transferir(desde, hacia, cantidad):
    result = {'correcto': False}
    envia = User.objects.get(username=desde)    
    enviaProfile = Profile.objects.get(usuario=envia)
    recibe = User.objects.get(username=hacia)
    recibeProfile = Profile.objects.get(usuario=recibe)
    conexionEnvia = EstadoConexion.objects.get(servidor=enviaProfile.subnet)
    conexionRecibe = EstadoConexion.objects.get(servidor=recibeProfile.subnet)
    if not conexionEnvia.online or not conexionRecibe.online:
        result['mensaje'] = "Sistema sin conexión, intente más tarde."
        return result
    if User.objects.filter(username=hacia).exists():
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
                contenido = f"Usted transfirió { cantidad } coins a { recibe.username }"
                notificacion = Notificacion(usuario=envia, tipo="ENVIO", contenido=contenido)
                notificacion.save() 
                contenido = f"Usted recibió { cantidad } coins de { envia.username }"
                notificacion = Notificacion(usuario=recibe, tipo="RECIBO", contenido=contenido)
                notificacion.save() 
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


