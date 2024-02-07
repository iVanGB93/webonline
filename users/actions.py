from django.contrib.auth.models import User
from users.models import Profile
from sync.models import EstadoConexion
import requests
import json


def check_user(user, email):
    response = {'state': False}
    servers = EstadoConexion.objects.all()
    for server in servers:
        url = f'http://{ server.ip_cliente }/api/users/user/{ user }/'
        data = json.dumps({'user': user, 'email': email})
        conexion = requests.get(url, data)
        if conexion.status_code != 200:
            response['message'] = 'Registro deshabilitado, intente más tarde.'
            return response
        if conexion.json()['message'] == 'user or email not found':
            response['state'] = True
        else:
            response['message'] = conexion.data.message
            return response
    return response
    
def check_email(email):
    servers = EstadoConexion.objects.all()
    for server in servers:
        url = f'http://{ server.ip_cliente }/api/users/email/{ email }/'
        conexion = requests.get(url)
        if conexion.status_code == 404:
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
