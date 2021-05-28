from django.utils import timezone
from datetime import datetime, timedelta
from .models import Recarga, Oper, EstadoServicio
from django.contrib.auth.models import User
from users.models import Profile
from django.core.mail import send_mail
from sync.syncs import actualizacion_remota
from decouple import config
import xml.etree.ElementTree
import subprocess
import hashlib
import requests
import paramiko
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

#FILEZILLA
user_xml_fmt = '''
        <User Name="{username}">
            <Option Name="Pass">{md5_pwd}</Option>
            <Option Name="Group">{group}</Option>
            <Option Name="Bypass server userlimit">2</Option>
            <Option Name="User Limit">0</Option>
            <Option Name="IP Limit">0</Option>
            <Option Name="Enabled">2</Option>
            <Option Name="Comments" />
            <Option Name="ForceSsl">2</Option>
            <IpFilter>
                <Disallowed />
                <Allowed />
            </IpFilter>
            <Permissions />
            <SpeedLimits DlType="0" DlLimit="10" ServerDlLimitBypass="2" UlType="0" UlLimit="10" ServerUlLimitBypass="2">
                <Download />
                <Upload />
            </SpeedLimits>
        </User>
'''

folder = 'C:/Program Files (x86)/FileZilla Server'
xml_path = os.path.join(folder, 'FileZilla Server.xml')
exe_path = os.path.join(folder, 'FileZilla Server.exe')

class DDDManager():

    def __init__(self, filename):
        self.filename = filename

    def setup(self):
        self.tree = xml.etree.ElementTree.parse(self.filename)
        self.root = self.tree.getroot()
        self.user_tree = self.root.findall('Users')[0]
        return self

    def new_user(self, username, pwd, group):
        pwd = pwd
        md5_pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
        xml_str = user_xml_fmt.format(username=username, md5_pwd=md5_pwd, group=group)
        return xml.etree.ElementTree.fromstring(xml_str)

    def add_user(self, *arg):
        user = self.new_user(*arg)        
        self.user_tree.append(user)

    def dump(self):
        self.tree.write(self.filename)

def activarFTP(username, pwd, group):

    manager = DDDManager(xml_path).setup() 

    manager.add_user(username, pwd, group)
    
    manager.dump()
    subprocess.run([exe_path, '/reload-config'], shell=True)
#Fin FILEZILLA

def comprar_internet(usuario, tipo, contra, horas):
    result = {'correcto': False, 'mensaje': ''}
    profile = Profile.objects.get(usuario=usuario)
    usuario = User.objects.get(username=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario.id)
    if servicio.internet == True:
        result['mensaje'] = 'Ya tiene el servicio activo.'
        return result
    if tipo == 'mensual':
        user_coins = int(profile.coins)
        if user_coins >= 200:
            profile.coins = profile.coins - 200
            perfil = config('INTERNET_PERFIL_MENSUAL_PORTAL')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(config('MK1_IP'), username=config('MK1_USER'), password=config('MK1_PASSWORD'))
                stdin, stdout, stderr = client.exec_command(f'/ip hotspot user set { usuario.username } disable="no" password={ contra } profile={ perfil } limit-uptime=0')
                for line in stdout:                
                    if "no such item" in line:
                        stdin, stdout, stderr = client.exec_command(f'/ip hotspot user add name={ usuario.username } password={ contra } profile={ perfil }')
                client.close()
                #crearLog(usuario.username, "ActivacionLOG.txt", f'Se activó correctamente el usuario: { usuario.username } al Mikrotik con prefil: { perfil }.')
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
            except:
                #crearLog("ERROR CON MIKROTIK", "ActivacionLOG.txt", f'Problema en la conexion con el mikrotik del usuario: { usuario.username }.') 
                result['mensaje'] = 'No se pudo conectar al mikrotik de internet.'
                return result
        else:
            result['mensaje'] = 'No tiene suficientes coins.'
            return result
    elif tipo == 'semanal':
        user_coins = int(profile.coins)
        if user_coins >= 300:
            profile.coins = profile.coins - 300
            perfil = config('INTERNET_PERFIL_SEMANAL')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(config('MK1_IP'), username=config('MK1_USER'), password=config('MK1_PASSWORD'))
                stdin, stdout, stderr = client.exec_command(f'/ip hotspot user set { usuario.username } disable="no" password={ contra } profile={ perfil } limit-uptime=0')
                for line in stdout:                
                    if "no such item" in line:
                        stdin, stdout, stderr = client.exec_command(f'/ip hotspot user add name={ usuario.username } password={ contra } profile={ perfil }')
                client.close()
                #crearLog(usuario.username, "ActivacionLOG.txt", f'Se activó correctamente el usuario: { usuario.username } al Mikrotik con prefil: { perfil }.')
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
            except:
                #crearLog("ERROR CON MIKROTIK", "ActivacionLOG.txt", f'Problema en la conexion con el mikrotik del usuario: { usuario.username }.') 
                result['mensaje'] = 'No se pudo conectar al mikrotik de internet.'
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
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    client.connect(config('MK1_IP'), username=config('MK1_USER'), password=config('MK1_PASSWORD'))
                    perfil = config('INTERNET_PERFIL_HORAS')
                    stdin, stdout, stderr = client.exec_command(f'/ip hotspot user set { usuario.username } password={ contra } profile={ perfil } limit-uptime={ horasMK } disable=no')
                    stdin, stdout, stderr = client.exec_command(f'/ip hotspot user reset-counters { usuario.username }')
                    for line in stdout:
                        if "no such item" in line:
                            stdin, stdout, stderr = client.exec_command(f'/ip hotspot user add name={ usuario.username } password={ contra } profile={ perfil } limit-uptime={ horasMK }')
                    code = crearOper(usuario.username, 'internetHoras', cantidad)
                    #crearLog(usuario.username, "ActivacionLOG.txt", f'Se actualizó correctamente el usuario: { usuario.username } en el Mikrotik con { horas} horas.')
                    client.close()            
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
                except:                
                    #crearLog("ERROR CON MIKROTIK", "ActivacionLOG.txt", f'Problema en la conexion con el mikrotik del usuario: { usuario.username }.')
                    result['mensaje'] = 'No se pudo conectar al mikrotik de internet.'
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
    if profile.coins >= 100:
        profile.coins = profile.coins - 100
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(config('MK2_IP'), username=config('MK2_USER'), password=config('MK2_PASSWORD'))
            stdin, stdout, stderr = client.exec_command(f'/ip firewall address-list set [find comment={usuario.username}] disable=no')
            client.close()
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
        except:
            result['mensaje'] = 'Error en el mikrotik de Joven Club.'
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
    if profile.coins >= 100:
        profile.coins = profile.coins - 100
        emby_ip = config('EMBY_IP')
        emby_api_key = config('EMBY_API_KEY')
        url = f'{ emby_ip }/Users/New?api_key={ emby_api_key }'
        json = {'Name': usuario.username}
        connect = requests.post(url=url, data=json)
        resp = connect.json()
        usuarioID = resp['Id']
        if connect.status_code == 200:
            profile.save()
            servicio.emby = True
            servicio.emby_id = usuarioID
            servicio.emby_time = timezone.now() + timedelta(days=30)
            servicio.sync = False
            servicio.save()
            url = f'{ emby_ip }/Users/{ usuarioID}/Configuration?api_key={ emby_api_key }'
            json = {
                        "PlayDefaultAudioTrack": True,
                        "DisplayMissingEpisodes": False,
                        "GroupedFolders": [],
                        "SubtitleMode": "Default",
                        "DisplayCollectionsView": False,
                        "EnableLocalPassword": False,
                        "OrderedViews": [],
                        "LatestItemsExcludes": [],
                        "MyMediaExcludes": [],
                        "HidePlayedInLatest": True,
                        "RememberAudioSelections": True,
                        "RememberSubtitleSelections": True,
                        "EnableNextEpisodeAutoPlay": True
                    }
            connect = requests.post(url=url, data=json)
            url = f'{ emby_ip }/Users/{ usuarioID}/Policy?api_key={ emby_api_key }'
            json = {
                        "IsAdministrator": False,
                        "IsHidden": True,
                        "IsHiddenRemotely": True,
                        "IsDisabled": False,
                        "BlockedTags": [],
                        "IsTagBlockingModeInclusive": False,
                        "EnableUserPreferenceAccess": True,
                        "AccessSchedules": [],
                        "BlockUnratedItems": [],
                        "EnableRemoteControlOfOtherUsers": False,
                        "EnableSharedDeviceControl": False,
                        "EnableRemoteAccess": False,
                        "EnableLiveTvManagement": False,
                        "EnableLiveTvAccess": False,
                        "EnableMediaPlayback": True,
                        "EnableAudioPlaybackTranscoding": True,
                        "EnableVideoPlaybackTranscoding": True,
                        "EnablePlaybackRemuxing": True,
                        "EnableContentDeletion": False,
                        "EnableContentDeletionFromFolders": [],
                        "EnableContentDownloading": False,
                        "EnableSubtitleDownloading": True,
                        "EnableSubtitleManagement": False,
                        "EnableSyncTranscoding": False,
                        "EnableMediaConversion": False,
                        "EnabledDevices": [],
                        "EnableAllDevices": True,
                        "EnabledChannels": [],
                        "EnableAllChannels": True,
                        "EnabledFolders": [],
                        "EnableAllFolders": True,
                        "InvalidLoginAttemptCount": 0,
                        "EnablePublicSharing": False,
                        "RemoteClientBitrateLimit": 0,
                        "AuthenticationProviderId": "Emby.Server.Implementations.Library.DefaultAuthenticationProvider",
                        "ExcludedSubFolders": [],
                        "SimultaneousStreamLimit": 1
                    }
            connect = requests.post(url=url, data=json)
            #crearLog(usuario.username, "ActivacionLOG.txt", f'Se agregó correctamente el usuario: { usuario.username } al Emby.')
            code = crearOper(usuario.username, "Emby", 100)
            send_mail('QbaRed - Pago confirmado', f'Gracias por utilizar nuestro servicio Emby, esperamos que disfrute sus 30 dias y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
            result['mensaje'] = 'Servicio activado con éxito.'
            result['correcto'] = True
            return result
        else:
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
    if profile.coins >= 50:
        profile.coins = profile.coins - 50
        activarFTP(usuario, contraseña, group='usuarios')
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