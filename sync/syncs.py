from decouple import config
import asyncio
import websockets
import json


#medula = config('MEDULA')
medula = 'ws://127.0.0.1:8080/ws/sync/'

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

def actualizacion_remota(accion, data):
    recibe = get_or_create_eventloop().run_until_complete(conectar(medula, accion, data))
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