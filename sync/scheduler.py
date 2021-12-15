from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone
from .models import EstadoConexion

from .syncs import actualizacion_remota

def chequeo_conexion_online():
    servidores = EstadoConexion.objects.all()
    for servidor in servidores:
        print(f"CHEQUEANDO A { servidor.servidor }")
        respuesta = actualizacion_remota('saludo', {'identidad': servidor.servidor})
        if respuesta['estado']:
            print("SERVIDOR ONLINE")
            servidor.online = True
        else:
            print("NO TIENE INTERNET EL SERVIDOR", respuesta['mensaje'])
            servidor.online = False
        servidor.save()

def chequeo_conexiones():
    scheduler = BackgroundScheduler()
    scheduler.add_job(chequeo_conexion_online, 'interval', minutes=3)
    scheduler.start()
