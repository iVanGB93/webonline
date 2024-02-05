from apscheduler.schedulers.background import BackgroundScheduler
from .models import EstadoConexion
import requests


def chequeo_conexion_online():
    servidores = EstadoConexion.objects.all()
    for servidor in servidores:
        print(f"CHEQUEANDO A { servidor.servidor }")
        url = f'http://{ servidor.ip_cliente }/api/sync/status/{servidor.servidor}/'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("SERVIDOR ONLINE")
                servidor.online = True
            else:
                print(f"NO TIENE INTERNET { servidor.servidor }")
                servidor.online = False
        except:
            print(f"NO TIENE INTERNET { servidor.servidor }")
            servidor.online = False
        servidor.save()

def chequeo_conexiones():
    scheduler = BackgroundScheduler()
    scheduler.add_job(chequeo_conexion_online, 'interval', minutes=3)
    scheduler.start()
