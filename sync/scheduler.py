from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
import os

from django.utils import timezone
from .syncs import actualizacion_remota
from .models import EstadoConexion

def chequeo_conexion_online():
    print("CHEQUEANDO SI ESTA ONLINE EL CLIENTE")
    servidor = config('NOMBRE_SERVIDOR')
    ip_cliente = config('IP_CLIENT')
    if EstadoConexion.objects.filter(id=1).exists():
        conexion = EstadoConexion.objects.get(id=1)
    else:
        conexion = EstadoConexion(id=1, servidor=servidor, ip_cliente=ip_cliente)
        conexion.ip_cliente = config('IP_CLIENT')        
    data = {'identidad': servidor}
    respuesta = actualizacion_remota('saludo', data)
    if respuesta['estado']:
        print("CLIENTE ONLINE")
        conexion.online = True
    else:
        print("NO TIENE INTERNET EL CLIENTE", respuesta['mensaje'])
        conexion.online = False
    conexion.save()


def chequeo_conexion_servicios():
    print("CHEQUEANDO LOS SERVICIOS")    
    conexion = EstadoConexion.objects.get(id=1)
    response = os.popen(f"ping { conexion.ip_internet }").read()
    if "recibidos = 4" in response:
        print("INTERNET ONLINE")
        conexion.internet = True
    else:
        print("INTERNET CAIDO")
        conexion.internet = False
    response = os.popen(f"ping { conexion.ip_jc }").read()
    if "recibidos = 4" in response:
        print("JC ONLINE")
        conexion.jc = True
    else:
        print("JC CAIDO")
        conexion.jc = False
    response = os.popen(f"ping { conexion.ip_emby }").read()
    if "recibidos = 4" in response:
        print("EMBY ONLINE")
        conexion.emby = True
    else:
        print("EMBY CAIDO")
        conexion.emby = False
    response = os.popen(f"ping { conexion.ip_ftp }").read()
    if "recibidos = 4" in response:
        print("FTP ONLINE")
        conexion.ftp = True
    else:
        print("FTP CAIDO")
        conexion.ftp = False
    conexion.fecha_internet = timezone.now()
    conexion.save()

#chequeo_conexion_online()


def chequeo_conexiones():
    scheduler = BackgroundScheduler()
    scheduler.add_job(chequeo_conexion_online, 'interval', minutes=4)
    #scheduler.add_job(chequeo_conexion_servicios, 'interval', minutes=40)
    scheduler.start()
