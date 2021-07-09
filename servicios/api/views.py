from servicios.models import Oper, Recarga, EstadoServicio
from users.models import Profile
from django.contrib.auth.models import User
from .serializers import OperSerializer, ServiciosSerializer
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta
from decouple import config
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

class ServiciosView(APIView):    

    def get(self, queryset=None, **kwargs):
        user = self.kwargs.get('pk')
        if User.objects.filter(username=user).exists():
            usuario = User.objects.get(username=user)
            servicios = EstadoServicio.objects.get(usuario=usuario.id)            
            serializer = ServiciosSerializer(servicios)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class InternetView(APIView):

    def get(self, queryset=None, **kwargs):        
        user = self.kwargs.get('pk')
        usuario = User.objects.get(username=user)
        servicio = EstadoServicio.objects.get(usuario=usuario.id)
        servicio.internet = False
        servicio.int_horas = 0
        servicio.save()
        return Response(status=status.HTTP_200_OK)

    """ def put(self, request, **kwargs):
        user = self.kwargs.get('pk')
        usuario = User.objects.get(username=user)
        profile = Profile.objects.get(usuario=usuario.id)
        servicio = EstadoServicio.objects.get(usuario=usuario.id)
        datos = request.data
        if 'int_horas' in request.data:            
            pwd = datos['contra']
            horas = datos['int_horas']
            horas = f'{horas}:00:00'
            cantidad = datos['cantidad']
            if profile.coins >= cantidad:
                profile.coins = profile.coins - cantidad
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)         
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(config('MK1_IP'), username=config('MK1_USER'), password=config('MK1_PASSWORD'))
                perfil = config('INTERNET_PERFIL_HORAS')
                stdin, stdout, stderr = client.exec_command(f'/ip hotspot user set { usuario.username } password={ pwd } profile={ perfil } limit-uptime={ horas } disable=no')
                stdin, stdout, stderr = client.exec_command(f'/ip hotspot user reset-counters { usuario.username }')
                for line in stdout:
                    if "no such item" in line:
                        stdin, stdout, stderr = client.exec_command(f'/ip hotspot user add name={ usuario.username } password={ pwd } profile={ perfil } limit-uptime={ horas }')
                code = crearOper(usuario.username, 'internetHoras', cantidad)
                crearLog(usuario.username, "ActivacionLOG.txt", f'Se actualizó correctamente el usuario: { usuario.username } en el Mikrotik con { horas} horas.')
                client.close()                               
                servicio.internet = True
                servicio.int_horas = datos['int_horas']
                servicio.int_time = None
                servicio.save()
                profile.save() 
                send_mail('Pago confirmado', f'Gracias por utilizar nuestro internet por horas, esperamos que disfrute sus { horas} horas y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                return Response(status=status.HTTP_200_OK)
            except:                
                crearLog("ERROR CON MIKROTIK", "ActivacionLOG.txt", f'Problema en la conexion con el mikrotik del usuario: { usuario.username }.')
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif 'servicio' in request.data:
            pwd = datos['contra'] 
            if datos['perfil'] == '1mb_para_PC2':
                perfil = config('INTERNET_PERFIL_SEMANAL')
            elif datos['perfil'] == 'LOCAL_1m':
                perfil = config('INTERNET_PERFIL_MENSUAL_PORTAL')                                    
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(config('MK1_IP'), username=config('MK1_USER'), password=config('MK1_PASSWORD'))
                stdin, stdout, stderr = client.exec_command(f'/ip hotspot user set { usuario.username } disable="no" password={ pwd } profile={ perfil } limit-uptime=0')
                for line in stdout:                
                    if "no such item" in line:
                        stdin, stdout, stderr = client.exec_command(f'/ip hotspot user add name={ usuario.username } password={ pwd } profile={ perfil }')
                client.close()
            except:
                crearLog("ERROR CON MIKROTIK", "ActivacionLOG.txt", f'Problema en la conexion con el mikrotik del usuario: { usuario.username }.') 
                return Response(status=status.HTTP_400_BAD_REQUEST)
            crearLog(usuario.username, "ActivacionLOG.txt", f'Se activó correctamente el usuario: { usuario.username } al Mikrotik con prefil: { perfil }.')               
            servicio.internet = True  
            servicio.int_tipo = datos['servicio']                
            if datos['servicio'] == 'internetSemanal':                
                servicio.int_time = timezone.now() + timedelta(days=7)
                if profile.coins >= 300:
                    profile.coins = profile.coins - 300
                    profile.save()
                    code = crearOper(usuario.username, datos['servicio'], 300)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            elif datos['servicio'] == 'internetMensual':                
                servicio.int_time = timezone.now() + timedelta(days=30)
                if profile.coins >= 200:
                    profile.coins = profile.coins - 200
                    profile.save()
                    code = crearOper(usuario.username, datos['servicio'], 200)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            servicio.save()
            send_mail('Pago confirmado', f'Gracias por utilizar nuestro { servicio.int_tipo }, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
            return Response(status=status.HTTP_200_OK)            
        elif 'int_auto' in request.data:                                                     
            servicio.int_auto = datos['int_auto']
            servicio.save()
            return Response(status=status.HTTP_200_OK)
        else:                                                    
            servicio.internet = datos['internet']
            send_mail('Internet desactivado', 'Se ha desactivado su acceso a Internet, terminaro su tiempo y no se ha renovado su suscripcion. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])        
            servicio.save()
            return Response(status=status.HTTP_200_OK) """

class JovenClubView(APIView):

    """ def put(self, request, **kwargs):
        user = self.kwargs.get('pk')
        usuario = User.objects.get(username=user)
        profile = Profile.objects.get(usuario=usuario.id)
        servicio = EstadoServicio.objects.get(usuario=usuario.id)
        datos= request.data
        if 'coins' in request.data:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(config('MK2_IP'), username=config('MK2_USER'), password=config('MK2_PASSWORD'))
                stdin, stdout, stderr = client.exec_command(f'/ip firewall address-list set [find comment={usuario.username}] disable=no')
                client.close()                              
                code = crearOper(usuario.username, "Joven-Club", 100)
                crearLog(usuario.username, "ActivacionLOG.txt", f'Se activó correctamente el usuario: { usuario.username } al Mikrotik Joven-Club.')
                if profile.coins >= 100:
                    profile.coins = profile.coins - 100
                    profile.save()
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                servicio.jc = True
                servicio.jc_time = timezone.now() + timedelta(days=30)
                servicio.save()
                send_mail('Pago confirmado', f'Gracias por utilizar nuestro servicio de Joven Club, esperamos que disfrute sus 30 dias y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                return Response(status=status.HTTP_200_OK)
            except:
                crearLog("ERROR CON MIKROTIK", "ActivacionLOG.txt", f'Problema en la conexion con el mikrotik JC del usuario: { usuario.username }.') 
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif 'jc_auto' in request.data:
            servicio.jc_auto = datos['jc_auto']
            servicio.save()
            return Response(status=status.HTTP_200_OK) 
        else:
            servicio.jc = datos['jc']
            send_mail('Joven Club desactivado', 'Se ha desactivado su acceso a Joven Club, terminaron sus 30 dias y no se ha renovado su suscripcion. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])        
            servicio.save()
            return Response(status=status.HTTP_200_OK) """

class EmbyView(APIView):

    """ def put(self, request, **kwargs):
        user = self.kwargs.get('pk')
        usuario = User.objects.get(username=user)
        profile = Profile.objects.get(usuario=usuario.id)
        servicio = EstadoServicio.objects.get(usuario=usuario.id)
        datos= request.data
        if 'coins' in request.data:
            emby_ip = config('EMBY_IP')            
            emby_api_key = config('EMBY_API_KEY')            
            url = f'{ emby_ip }/Users/New?api_key={ emby_api_key }'
            json = {'Name': usuario.username}  
            connect = requests.post(url=url, data=json)          
            resp = connect.json()    
            usuarioID = resp['Id']            
            if connect.status_code == 200:
                if profile.coins >= 100:
                    profile.coins = profile.coins - 100
                    profile.save()
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                servicio.emby = True
                servicio.emby_id = usuarioID
                servicio.emby_time = timezone.now() + timedelta(days=30)
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
                crearLog(usuario.username, "ActivacionLOG.txt", f'Se agregó correctamente el usuario: { usuario.username } al Emby.')
                code = crearOper(usuario.username, "Emby", 100)
                send_mail('Pago confirmado', f'Gracias por utilizar nuestro servicio Emby, esperamos que disfrute sus 30 dias y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'emby_auto' in request.data:
            servicio.emby_auto = datos['emby_auto']
            servicio.save()
            return Response(status=status.HTTP_200_OK)
        else:
            servicio.emby = datos['emby']
            servicio.save()
            send_mail('Emby desactivado', 'Se ha desactivado su cuenta del Emby, terminaron sus 30 dias y no se ha renovado su suscripcion. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])            
            return Response(status=status.HTTP_200_OK) """

class FileZillaView(APIView):

    """ def put(self, request, **kwargs):
        user = self.kwargs.get('pk')
        usuario = User.objects.get(username=user)
        profile = Profile.objects.get(usuario=usuario.id)
        servicio = EstadoServicio.objects.get(usuario=usuario.id)
        datos= request.data
        if 'contra' in request.data:
            if profile.coins >= 50:
                profile.coins = profile.coins - 50
                activarFTP(usuario.username, datos['contra'], group='usuarios')
                profile.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            servicio.ftp = True
            servicio.ftp_time = timezone.now() + timedelta(days=30)
            code = crearOper(usuario.username, 'FileZilla', 50)
            crearLog(usuario.username, "ActivacionLOG.txt", f'El usuario: { usuario.username } pago por FTP.')
            send_mail('Pago confirmado', f'Gracias por utilizar nuestro servicio de FileZilla, esperamos que disfrute sus 30 dias y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])            
            servicio.save()            
            return Response(status=status.HTTP_200_OK)
        elif 'ftp_auto' in request.data:
            servicio.ftp_auto = datos['ftp_auto']
            servicio.save()
            return Response(status=status.HTTP_200_OK)
        else:
            servicio.ftp = datos['ftp']
            send_mail('FileZilla desactivado', 'Se ha desactivado su cuenta de FileZilla, terminaron sus 30 dias y no se ha renovado su suscripcion. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])        
            servicio.save()
            return Response(status=status.HTTP_200_OK) """

class OperView(APIView):  

    def get(self, request, format=None, **kwargs):
        username = self.kwargs.get('pk')
        if User.objects.filter(username=username).exists():
            usuario = User.objects.get(username=username)
            opers = Oper.objects.filter(usuario=usuario.id).order_by('-fecha')[:10]
            serializer = OperSerializer(opers, many=True)            
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class RecargaView(APIView):

    def post(self, request, format=None, **kwargs):
        code = self.kwargs.get('pk')
        username = request.data['usuario']       
        if Recarga.objects.filter(code=code).exists():
            recarga = Recarga.objects.get(code=code)
            usuario = User.objects.get(username=username)
            profile = Profile.objects.get(usuario=usuario.id)
            if recarga.activa:
                cantidad = recarga.cantidad                
                profile.coins = profile.coins + cantidad
                profile.save()
                recarga.activa = False
                recarga.fechaUso = timezone.now()
                recarga.usuario = usuario
                recarga.save()
                oper = Oper(tipo='RECARGA', usuario=usuario, codRec=code, cantidad=cantidad)
                oper.save()
                json = {'mensaje': 'Cuenta Recargada con éxito'}
                return Response(data=json, status=status.HTTP_200_OK)
            else:
                json = {'mensaje': 'Recarga usada'}
                return Response(data=json, status=status.HTTP_208_ALREADY_REPORTED)
        else:
            json = {'mensaje': 'Recarga incorrecta'}
            return Response(data=json, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

class TransferView(APIView):

    def get(self, request, format=None, **kwargs):
        username = self.kwargs.get('pk')       
        if User.objects.filter(username=username).exists():
            return Response(status=status.HTTP_200_OK)
        else:            
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, format=None, **kwargs):
        username = self.kwargs.get('pk')
        data = request.data
        usuario = data['usuario']
        cantidad = data['cantidad']
        envia = User.objects.get(username=username)
        recibe = User.objects.get(username=usuario)        
        enviaProfile = Profile.objects.get(usuario=envia.id)
        recibeProfile = Profile.objects.get(usuario=recibe.id)
        if enviaProfile.coins >= cantidad:
            recibeProfile.coins = recibeProfile.coins + cantidad
            recibeProfile.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        oper = Oper(usuario=recibe, tipo="RECIBO", cantidad=cantidad, haciaDesde=username)
        oper.save()
        enviaProfile.coins = enviaProfile.coins - cantidad
        enviaProfile.save()
        cantidad = cantidad * -1
        oper = Oper(usuario=envia, tipo="ENVIO", cantidad=cantidad, haciaDesde=usuario)
        oper.save()
        json={'mensaje': 'Transferencia realizada con éxito'}
        return Response(data=json, status=status.HTTP_200_OK)