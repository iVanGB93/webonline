from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone
from .models import EstadoConexion

def chequeo_conexion_online():
    servidores = EstadoConexion.objects.all()
    for servidor in servidores:
        tiempo = timezone.now() - timezone.timedelta(seconds=185)
        print(f"CHEQUEANDO A { servidor.servidor }")
        if servidor.fecha_chequeo < tiempo:
            servidor.online = False
            servidor.save()
            print(f"EL SERVIDOR { servidor.servidor } ESTA CAIDO DESDE { servidor.fecha_chequeo }.")
        else:
            print(f"EL SERVIDOR { servidor.servidor } ESTA ONLINE.")


def chequeo_conexiones():
    scheduler = BackgroundScheduler()
    scheduler.add_job(chequeo_conexion_online, 'interval', minutes=3)
    scheduler.start()
