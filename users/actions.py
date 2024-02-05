from decouple import config
import requests
import json

url_client = config('IP_CLIENT')

def check_user(user, email):
    response = {'state': False}
    url = f'http://{ url_client }/api/users/user/{ user }/'
    data = json.dumps({'user': user, 'email': email})
    conexion = requests.get(url, data)
    if conexion.status_code != 200:
        response['message'] = 'Registro deshabilitado, intente más tarde.'
        return response
    if conexion.json()['message'] == 'user or email not found':
        response['state'] = True
        return response
    else:
        response['message'] = conexion.data.message
        return response  
    
def check_email(email):
    url = f'http://{ url_client }/api/users/email/{ email }/'
    conexion = requests.get(url)
    if conexion.status_code == 200:
        return True
    elif conexion.status_code == 404:
        return False
    else:
        return conexion

def create_user(username, email, password):
    response = {'state': False}
    url = f'http://{ url_client }/api/users/newuser/'
    data = {'username': username, 'email': email, 'password': password}
    conexion = requests.get(url, json=data)
    if conexion.status_code == 200:
        response['state'] = True
        return response
    else:
        response['message'] = conexion
        return response
