from .models import  Oper
from django.contrib.auth.models import User
from decouple import config
from datetime import datetime
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