from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from django.utils import timezone
from .models import EstadoServicio, Oper
from users.models import Profile
from django.contrib.auth.models import User
from decouple import config
from datetime import datetime, timedelta
import paramiko
import requests
import xml.etree.ElementTree
import subprocess
import hashlib
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

def quitarMk(ip, comando):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=config('MK1_USER'), password=config('MK1_PASSWORD'))
        stdin, stdout, stderr = client.exec_command(comando)
        for line in stdout:            
            if "no such item" in line:
                return False
        client.close()
        return True
    except:
        crearLog("ERROR CON MIKROTIK", "DesActivacionLOG.txt", f'Problema en la conexion con el mikrotik para desactivar un usuario.')
        return False

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

    def remove_user(self, username):
        for user in self.user_tree:
            if user.get('Name') == username:
                self.user_tree.remove(user)

    def dump(self):
        self.tree.write(self.filename)

def quitarFTP(username):

    manager = DDDManager(xml_path).setup()   
   
    manager.remove_user(username)

    manager.dump()
    subprocess.run([exe_path, '/reload-config'], shell=True)
#Fin FileZilla

def chequeoInternet():    
    inter = EstadoServicio.objects.filter(internet=True)
    for i in inter:   
        exp = i.int_time
        if exp:
            if exp <= timezone.now():
                usuario = User.objects.get(username=i.usuario)
                profile = Profile.objects.get(usuario=usuario.id)
                if i.int_auto:                    
                    if i.int_tipo == "internetSemanal":
                        if profile.coins >= 300:
                            profile.coins = profile.coins - 300
                            i.int_time = timezone.now() + timedelta(days=7)
                            profile.sync = False
                            profile.save()
                            i.sync = False
                            i.save()
                            code = crearOper(usuario.username, "internetSemanal", 300)
                            send_mail('QbaRed - Pago confirmado', f'Se ha reanudado su servicio { i.int_tipo }, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                        else:
                            comando = f'/ip hotspot user set { usuario.username } disable=yes'
                            if quitarMk(config('MK1_IP'), comando):                            
                                crearLog(usuario.username, "DesactivacionLOG.txt", f'Se desactivó correctamente al usuario: { usuario.username } el internet.')        
                            else:
                                crearLog(usuario.username, "DesactivacionLOG.txt", f'No se encontro al usuario: { usuario.username } para desactivarle el internet.')
                            i.internet = False
                            i.int_auto = False
                            i.sync = False
                            i.save()
                            send_mail('QbaRed - Rechazo de pago', f'No se pudo reanudar su servicio { i.int_tipo }, no tiene suficientes coins, por favor recargue. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                    if i.int_tipo == "internetMensual":
                        if profile.coins >= 200:
                            profile.coins = profile.coins - 200
                            i.int_time = timezone.now() + timedelta(days=30)
                            profile.sync = False
                            profile.save()
                            i.sync = False
                            i.save()
                            code = crearOper(usuario.username, "internetMensual", 200)
                            send_mail('QbaRed - Pago confirmado', f'Se ha reanudado su servicio { i.int_tipo }, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                        else:
                            comando = f'/ip hotspot user set { usuario.username } disable=yes'
                            if quitarMk(config('MK1_IP'), comando):
                                crearLog(usuario.username, "DesactivacionLOG.txt", f'Se desactivó correctamente al usuario: { usuario.username } el internet.')        
                            else:
                                crearLog(usuario.username, "DesactivacionLOG.txt", f'No se encontro al usuario: { usuario.username } para desactivarle el internet.')
                            i.internet = False
                            i.int_auto = False
                            i.sync = False
                            i.save()
                            send_mail('QbaRed - Rechazo de pago', f'No se pudo reanudar su servicio { i.int_tipo }, no tiene suficientes coins, por favor recargue. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                else:                    
                    comando = f'/ip hotspot user set { usuario.username } disable=yes'
                    if quitarMk(config('MK1_IP'), comando):
                        crearLog(usuario.username, "DesactivacionLOG.txt", f'Se desactivó correctamente al usuario: { usuario.username } el internet.')        
                    else:
                        crearLog(usuario.username, "DesactivacionLOG.txt", f'No se encontro al usuario: { usuario.username } para desactivarle el internet.')                
                    i.internet = False
                    i.sync = False
                    i.save()
                    send_mail('QbaRed - Tiempo agotado', f'Se termino el tiempo del { i.int_tipo }, para volver a usarlo vaya a nuestro portal del usuario. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])    

def chequeo():    
    emb = EstadoServicio.objects.filter(emby=True)
    jclub = EstadoServicio.objects.filter(jc=True)
    filezilla = EstadoServicio.objects.filter(ftp=True)    
    for e in emb: 
        exp = e.emby_time
        if exp:
            if exp <= timezone.now():
                usuario = User.objects.get(username=e.usuario)
                profile = Profile.objects.get(usuario=usuario.id)
                emby_ip = config('EMBY_IP')            
                emby_api_key = config('EMBY_API_KEY')            
                url = f'{ emby_ip }/Users/{ e.emby_id }?api_key={ emby_api_key }' 
                if e.emby_auto:                    
                    if profile.coins >= 100:
                        profile.coins = profile.coins - 100
                        profile.sync = False
                        profile.save()
                        e.emby_time = timezone.now() + timedelta(days=30)
                        e.sync = False
                        e.save()
                        code = crearOper(usuario.username, "Emby", 100)
                        send_mail('QbaRed - Pago confirmado', f'Se ha reanudado su servicio emby, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                    else:
                        send_mail('QbaRed - Rechazo de pago', 'No se pudo reanudar su servicio emby, no tiene suficientes coins, por favor recargue. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])                       
                        connect = requests.delete(url=url)
                        if connect.status_code == 200:
                            crearLog(usuario.username, "DesactivacionLOG.txt", f'Se eliminó correctamente al usuario: { usuario.username } del Emby.')
                            e.emby = False
                            e.emby_auto = False
                            e.sync = False
                            e.save()
                        else:           
                            crearLog(usuario.username, "DesactivacionLOG.txt", f'Problema en la desactivacion del Emby.')
                            send_mail(f'Quitar Emby a { usuario.username }', f'Tiempo acabado y no se desactiva su cuenta.', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])
                else:
                    send_mail('QbaRed - Tiempo agotado', 'Se terminó el tiempo de su servicio emby, para volver a usarlo vaya a nuestro portal del usuario. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                    connect = requests.delete(url=url)
                    if connect.status_code == 200:
                        crearLog(usuario.username, "DesactivacionLOG.txt", f'Se eliminó correctamente al usuario: { usuario.username } del Emby.')
                        e.emby = False
                        e.sync = False
                        e.save()
                    else:                                 
                        crearLog(usuario.username, "DesactivacionLOG.txt", f'Problema en la desactivacion del Emby.')
                        send_mail(f'Quitar Emby a { usuario.username }', f'Tiempo acabado y no se desactiva su cuenta.', 'RedCentroHabanaCuba@gmail.com', ['ivanguachbeltran@gmail.com'])
    for j in jclub:   
        exp = j.jc_time
        if exp:
            if exp <= timezone.now():
                usuario = User.objects.get(username=j.usuario)
                profile = Profile.objects.get(usuario=usuario.id)
                if j.jc_auto:                    
                    if profile.coins >= 100:
                        profile.coins = profile.coins - 100
                        profile.sync = False
                        profile.save()
                        j.jc_time = timezone.now() + timedelta(days=30)
                        j.sync = False
                        j.save()
                        code = crearOper(usuario.username, "Joven Club", 100)
                        send_mail('QbaRed - Pago confirmado', f'Se ha reanudado su servicio JovenClub, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                    else:
                        comando = f'/ip firewall address-list set [find comment={usuario.username}] disable=yes'
                        if quitarMk(config('MK2_IP'), comando):
                            crearLog(usuario.username, "DesactivacionLOG.txt", f'Se desactivó correctamente al usuario: { usuario.username } el Joven-Club.')
                        else:
                            crearLog(usuario.username, "DesactivacionLOG.txt", f'No se encontro al usuario: { usuario.username } para desactivarle el Joven-Club.')
                        j.jc = False
                        j.jc_auto = False
                        j.sync = False
                        j.save()
                        send_mail('QbaRed - Rechazo de pago', 'No se pudo reanudar su servicio JovenClub, no tiene suficientes coins, por favor recargue. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                else:
                    comando = f'/ip firewall address-list set [find comment={usuario.username}] disable=yes'
                    if quitarMk(config('MK2_IP'), comando):
                        crearLog(usuario.username, "DesactivacionLOG.txt", f'Se desactivó correctamente al usuario: { usuario.username } el Joven-Club.')
                    else:    
                        crearLog(usuario.username, "DesactivacionLOG.txt", f'No se encontro al usuario: { usuario.username } para desactivarle el Joven-Club.')
                    j.jc = False
                    j.jc_auto = False
                    j.sync = False
                    j.save()
                    send_mail('QbaRed - Tiempo agotado', 'Se termino el tiempo de su servicio Joven Club, para volver a usarlo vaya a nuestro portal del usuario. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
    for f in filezilla:   
        exp = f.ftp_time       
        if exp:
            if exp <= timezone.now():
                usuario = User.objects.get(username=f.usuario)
                profile = Profile.objects.get(usuario=usuario.id)                
                if f.ftp_auto:
                    if profile.coins >= 50:
                        profile.coins = profile.coins - 50
                        profile.sync = False
                        profile.save()
                        f.ftp_time = timezone.now() + timedelta(days=30)
                        f.sync = False
                        f.save()
                        code = crearOper(usuario.username, "FileZilla", 50)
                        send_mail('QbaRed - Pago confirmado', f'Se ha reanudado su servicio FileZilla, esperamos que disfrute su tiempo y que no tenga mucho tufe la red ;-) Utilice este código para el sorteo mensual: "{ code }". Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                    else:
                        quitarFTP(usuario.username)                          
                        f.ftp = False
                        f.ftp_auto = False
                        f.sync = False
                        f.save() 
                        send_mail('QbaRed - Rechazo de pago', 'No se pudo reanudar su servicio FileZilla, no tiene suficientes coins, por favor recargue. Saludos QbaRed.', 'RedCentroHabanaCuba@gmail.com', [usuario.email])
                        crearLog(usuario.username, "DesActivacionLOG.txt", f'Se elimino de FileZilla a: { usuario.username }.')               
                else:
                    quitarFTP(usuario.username)                          
                    f.ftp = False
                    f.sync = False
                    f.save()               
                    crearLog(usuario.username, "DesActivacionLOG.txt", f'Se elimino de FileZilla a: { usuario.username }.')               

def tiempoAcabado():
    scheduler = BackgroundScheduler()
    scheduler.add_job(chequeoInternet, 'interval', minutes=5)
    scheduler.add_job(chequeo, 'interval', minutes=30)
    scheduler.start()