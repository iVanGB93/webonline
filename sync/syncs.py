from .models import EstadoConexion
import asyncio
import websockets
import json


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

def actualizacion_remota(accion, data):
    subnet = data.get('server', 'local_iVan')
    conexion = EstadoConexion.objects.get(servidor=subnet)
    ip = conexion.ip_cliente
    url = f'ws://{ ip }/ws/sync/'
    print(url)
    recibe = get_or_create_eventloop().run_until_complete(conectar(url, accion, data))
    return recibe

async def conectar(url, accion, data):
    respuesta = {'conexion': False, 'estado': False}
    try:
        async with websockets.connect(url) as ws:
            while True:
                envia = json.dumps({'accion': accion, 'data': data})
                await ws.send(envia)
                recibe = await ws.recv()
                respuesta = json.loads(recibe)
                respuesta['conexion'] = True
                return respuesta
    except ConnectionRefusedError:
        respuesta['mensaje'] = 'EL SERVIDOR DENEGO LA CONEXION'
        return respuesta
    except OSError:
        respuesta['mensaje'] = f'IP INALCANZABLE { OSError }'
        return respuesta
    except TypeError:
        respuesta['mensaje'] = f'ERROR {TypeError}'
    except:
        respuesta['mensaje'] = 'NADA QUE DECIR, SOLO PROBLEMAS'
        return respuesta