from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Sorteo
from servicios.models import Oper
from users.models import Notificacion

def crear_participacion(usuario, code, servicio, sync):
    resultado = {'estado': False}
    if Sorteo.objects.filter(code=code).exists():
        resultado['mensaje'] = 'Ya esta participación está creada.'
        return resultado
    participacion = Sorteo(usuario=usuario, code=code, servicio=servicio)
    participacion.sync = sync
    participacion.save()
    resultado['estado'] = True
    resultado['mensaje'] = 'Participación agregada con éxito.'
    return resultado

def participacion(code):
    resultado = {'estado': False}
    if Oper.objects.filter(code=code).exists():
        oper = Oper.objects.get(code=code)
        ahora = timezone.now()
        if oper.fecha.month != ahora.month:
            resultado['mensaje'] = 'Código debe ser del mes actual'
            return resultado
        if Sorteo.objects.filter(code=code).exists():
            resultado['mensaje'] = 'Código usado'
            return resultado        
        if oper.tipo != "PAGO":
            resultado['mensaje'] = 'Código debe ser de algún pago'
            return resultado
        if oper.servicio == "internetHoras":
            if oper.cantidad < 100:               
                resultado['mensaje'] = 'Código solo de pago de 10 horas o más.'
                return resultado                          
        participacion = crear_participacion(oper.usuario, code, oper.servicio, False)
        if not participacion['estado']:
            resultado['mensaje'] = participacion['mensaje']
            return resultado
        usuario = User.objects.get(username=oper.usuario)
        send_mail('Sorteo QbaRed', f'Usted esta participando en el sorteo de QbaRed con el código {code}, obtenido por el servicio {oper.servicio}. Suerte!!!', None, [usuario.email])
        send_mail('Sorteo QbaRed', f'Se registro {usuario.username} con  el código {code}, obtenido por el servicio {oper.servicio}.', None, ['ivanguachbeltran@gmail.com'])
        dato = f"Participación en el sorteo guardada, código { code }"
        notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido=dato)
        notificacion.save()
        resultado['estado'] = True
        resultado['mensaje'] = 'Se ha agregado su participación.'
        return resultado
    else:
        resultado['mensaje'] = 'Código incorrecto.'
        return resultado
                    