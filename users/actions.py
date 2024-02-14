from django.contrib.auth.models import User
from users.models import Profile
from sync.models import EstadoConexion
from decouple import config
import requests
import json


def check_user(user, email):
    response = {'state': False}
    servers = EstadoConexion.objects.all()
    for server in servers:
        if config('NOMBRE_SERVIDOR') == 'core_ONLINE':
            ip = server.ip_cliente
        else:
            ip = server.ip_online
        url = f'http://{ ip }/api/users/user/{ user }/'
        data = json.dumps({'user': user, 'email': email})
        try:
            conexion = requests.get(url, data)
            if conexion.status_code != 200:
                response['message'] = 'Registro deshabilitado, intente más tarde.'
                return response
            if conexion.json()['message'] == 'user or email not found':
                response['state'] = True
            else:
                response['message'] =  conexion.json()['message']
                return response
        except:
            response['message'] = 'Servidor local sin conexion, intente mas tarde.'
            return response
    return response
    
def check_email(email):
    servers = EstadoConexion.objects.all()
    for server in servers:
        if config('NOMBRE_SERVIDOR') == 'core_ONLINE':
            ip = server.ip_cliente
        else:
            ip = server.ip_online
        url = f'http://{ ip }/api/users/email/{ email }/'
        try:
            conexion = requests.get(url)
            if conexion.status_code == 404:
                return False
        except:
            return False
    return True

def create_user(username, email, password):
    response = {'state': False}
    user = User.objects.get(username=username)
    profile = Profile.objects.get(usuario=user)
    localServer = EstadoConexion.objects.get(servidor=profile.subnet)
    url = f'http://{ localServer.ip_cliente }/api/users/newuser/'
    data = {'username': username, 'email': email, 'password': password}
    try:
        conexion = requests.get(url, json=data)
        if conexion.status_code == 200:
            response['state'] = True
            return response
        else:
            response['message'] = 'Servidor local sin conexion, intente mas tarde.'
            return response
    except:
        response['message'] = 'Servidor local sin conexion, intente mas tarde.'
        return response
