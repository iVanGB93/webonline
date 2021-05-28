from django.utils import timezone
from datetime import datetime, timedelta
from .models import Recarga, Oper, EstadoServicio
from django.contrib.auth.models import User
from users.models import Profile
from django.core.mail import send_mail
from sync.syncs import actualizacion_remota
from decouple import config
import requests
import os

def crearLog(usuario, nombre, texto):
    dir = os.path.join("C:\\","WEB", "LOG", usuario)
    if not os.path.exists(dir):
        os.mkdir(dir)
    log = open(f'c:/WEB/LOG/{usuario}/{nombre}', "a")
    log.write('\n' + texto + '  fecha: ' + datetime.now().strftime(' %d-%b-%Y  Hora: %H:%M'))
    log.close()

def crearOper(usuario, servicio, cantidad):
    userinst = User.objects.get(username=usuario)           
    nuevaOper = Oper(tipo='PAGO', usuario=userinst, servicio=servicio, cantidad=cantidad)
    nuevaOper.save()
    code = nuevaOper.code
    return code

def comprar_internet(usuario, tipo, contra, horas):
    result = {'correcto': False, 'mensaje': ''}
    profile = Profile.objects.get(usuario=usuario)
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.internet == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    result['mensaje'] = 'NO ESTA ACTIVADA LA COMPRA DESDE INTERNET AUN.'
    return result
    if tipo == 'mensual':
        user_coins = int(profile.coins)
        if user_coins >= 200:
            profile.coins = profile.coins - 200
            perfil = config('INTERNET_PERFIL_MENSUAL_PORTAL')            
            servicio.internet = True  
            servicio.int_time = timezone.now() + timedelta(days=30)
            servicio.int_tipo = 'internetMensual'
            servicio.sync = False
            servicio.save()
            profile.save()
            code = crearOper(usuario.username, 'internetMensual', 200)
            send_mail('QbaRed - Pago confirmado', f'Gracias por utilizar nuestro { servicio.int_tipo }, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
            result['mensaje'] = 'Servicio activado con éxito.'
            result['correcto'] = True
            return result           
        else:
            result['mensaje'] = 'No tiene suficientes coins.'
            return result
    elif tipo == 'semanal':
        user_coins = int(profile.coins)
        if user_coins >= 300:
            profile.coins = profile.coins - 300            
            servicio.internet = True  
            servicio.int_time = timezone.now() + timedelta(days=7)
            servicio.int_tipo = 'internetSemanal'
            servicio.sync = False
            servicio.save()
            profile.save()
            code = crearOper(usuario.username, 'internetSemanal', 300)
            send_mail('QbaRed - Pago confirmado', f'Gracias por utilizar nuestro { servicio.int_tipo }, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
            result['mensaje'] = 'Servicio activado con éxito.'
            result['correcto'] = True
            return result                     
        else:
            result['mensaje'] = 'No tiene suficientes coins.'
            return result
    elif tipo == 'horas':
        try:
            cantidad_horas = int(horas)
            if cantidad_horas <5:
                result['mensaje'] = 'Mínimo 5 horas.'
                return result
            cantidad = cantidad_horas * 10
            horasMK = f'{horas}:00:00'
            user_coins = int(profile.coins)
            if user_coins >= cantidad:
                profile.coins = profile.coins - cantidad
                servicio.internet = True
                servicio.int_horas = horas
                servicio.int_tipo = 'internetHoras'
                servicio.int_time = None
                servicio.sync = False
                servicio.save()
                profile.save() 
                send_mail('QbaRed - Pago confirmado', f'Gracias por utilizar nuestro internet por horas, esperamos que disfrute sus { horas} horas y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                result['mensaje'] = 'Servicio activado con éxito.'
                result['correcto'] = True
                return result                
            else:
                result['mensaje'] = 'No tiene suficientes coins.'
                return result
        except ValueError:
            result['mensaje'] = 'Defina bien las horas'
            return result
    else:
        result['mensaje'] = 'Error de solicitud'
        return result

def comprar_jc(usuario):
    result = {'correcto': False, 'mensaje': ''}
    profile = Profile.objects.get(usuario=usuario)
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    result['mensaje'] = 'NO ESTA ACTIVADA LA COMPRA DESDE INTERNET AUN.'
    return result
    if profile.coins >= 100:
        profile.coins = profile.coins - 100        
        profile.save()
        servicio.jc = True
        servicio.jc_time = timezone.now() + timedelta(days=30)
        servicio.sync = False
        servicio.save()
        code = crearOper(usuario.username, "Joven-Club", 100)
        send_mail('QbaRed - Pago confirmado', f'Gracias por utilizar nuestro servicio de Joven Club, esperamos que disfrute sus 30 dias y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
        #crearLog(usuario.username, "ActivacionLOG.txt", f'Se activó correctamente el usuario: { usuario.username } al Mikrotik Joven-Club.')
        result['mensaje'] = 'Servicio activado con éxito.'
        result['correcto'] = True
        return result        
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def comprar_emby(usuario):
    result = {'correcto': False, 'mensaje': ''}
    profile = Profile.objects.get(usuario=usuario)
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    result['mensaje'] = 'NO ESTA ACTIVADA LA COMPRA DESDE INTERNET AUN.'
    return result
    if profile.coins >= 100:
        profile.coins = profile.coins - 100       
        result['mensaje'] = 'Error en el servidor Emby.'
        return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def comprar_filezilla(usuario, contraseña):
    result = {'correcto': False, 'mensaje': ''}
    profile = Profile.objects.get(usuario=usuario)
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario)
    if servicio.jc == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    result['mensaje'] = 'NO ESTA ACTIVADA LA COMPRA DESDE INTERNET AUN.'
    return result
    if profile.coins >= 50:
        profile.coins = profile.coins - 50        
        profile.save()
        servicio.ftp = True
        servicio.ftp_time = timezone.now() + timedelta(days=30)
        code = crearOper(usuario.username, 'FileZilla', 50)
        #crearLog(usuario, "ActivacionLOG.txt", f'El usuario: { usuario.username } pago por FTP.')
        send_mail('QbaRed - Pago confirmado', f'Gracias por utilizar nuestro servicio de FileZilla, esperamos que disfrute sus 30 dias y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])            
        servicio.sync = False
        servicio.save()
        result['mensaje'] = 'Servicio activado con éxito.'
        result['correcto'] = True
        return result
    else:
        result['mensaje'] = 'No tiene suficientes coins.'
        return result

def recargar(code, usuario):
    result = {'correcto': False, 'mensaje': ''}
    result['mensaje'] = 'NO ESTA ACTIVADA LA RECARGA DESDE INTERNET AUN.'
    return result
    if Recarga.objects.filter(code=code).exists():
        recarga = Recarga.objects.get(code=code)        
        if recarga.activa:
                usuario = User.objects.get(username=usuario)
                profile = Profile.objects.get(usuario=usuario.id)
                cantidad = recarga.cantidad                   
                profile.coins = profile.coins + cantidad
                respuesta = actualizacion_remota('usar_recarga', {'usuario': usuario.username, 'code': code})
                if respuesta['estado']:                    
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
                    result['mensaje'] = respuesta['mensaje']
                    return result
        else:
            result['mensaje'] = 'Recarga usada'
            return result
    else:
        result['mensaje'] = 'Recarga incorrecta'
        return result

def transferir(desde, hacia, cantidad):
    result = {'correcto': False, 'mensaje': ''}
    result['mensaje'] = 'NO ESTA ACTIVADA LA TRANSFERENCIA DESDE INTERNET AUN.'
    return result
    if User.objects.filter(username=hacia).exists():
        envia = User.objects.get(username=desde)        
        enviaProfile = Profile.objects.get(usuario=envia.id)        
        coinsDesde = int(enviaProfile.coins)        
        if coinsDesde >= cantidad:
            if cantidad >= 20:
                recibe = User.objects.get(username=hacia)
                recibeProfile = Profile.objects.get(usuario=recibe.id)
                recibeProfile.coins = recibeProfile.coins + cantidad
                enviaProfile.coins = enviaProfile.coins - cantidad 
                enviaProfile.sync = False     
                enviaProfile.save()
                recibeProfile.sync = False
                recibeProfile.save()
                cantidad = str(cantidad)
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
            result['mensaje'] = 'Su cantidad es insufuciente'
            return result
    else:
        result['mensaje'] = 'El usuario de destino no existe'
        return result