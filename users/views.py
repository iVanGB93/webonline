from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from users.models import Profile
from sync.models import EstadoConexion
from servicios.models import EstadoServicio
from sync.syncs import actualizacion_remota
from sync.actions import UpdateThreadUsuario
from .actions import check_user
from decouple import config


def entrar(request):
    if request.user.is_authenticated:
        return redirect ('web:index')
    if request.method == 'POST':
        content = {'icon': 'error'}
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('web:index')
            else:
                content['mensaje'] = "Contraseña Incorrecta"
                return render(request, 'users/login.html', content)            
        else:
            if config('NOMBRE_SERVIDOR') != 'core_ONLINE':
                check_user = actualizacion_remota('check_usuario', {'usuario': username})
                if not check_user['conexion']:
                    content['mensaje'] = "Servidor sin conexion, intente mas tarde."
                    return render(request, 'users/login.html', content)
                if check_user['estado']:
                    content['mensaje'] = "Su usuario no se encuentra en la local."
                    send_username = username
                    return redirect('users:pullUser', user=send_username)
            else:
                content['mensaje'] = "Usuario no existe"
                return render(request, 'users/login.html', content)
    else:
        return render(request, 'users/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect ('web:index')
    content = {'icon': 'error'}
    if request.method == 'POST':
        if config('NOMBRE_SERVIDOR') == 'core_ONLINE':
            conexion = EstadoConexion.objects.get(servidor=request.POST['subnet'])
        else:
            conexion = EstadoConexion.objects.get(servidor=config('NOMBRE_SERVIDOR'))
        if not conexion.online:
            content['mensaje'] = "Registro deshabilitado, intente más tarde."
            return render(request, 'users/register.html', content)
        password = request.POST['password']
        if len(password) <8:
            content['mensaje'] = "Contraseña mínimo 8 caracteres."
            return render(request, 'users/register.html', content)
        password2 = request.POST['passwordConfirm']
        if password != password2:
            content['mensaje'] = "Las contraseñas no coinciden."
            return render(request, 'users/register.html', content)
        email = request.POST['email']
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            content['mensaje'] = "Nombre de usuario en uso."
            return render(request, 'users/register.html', content)
        if User.objects.filter(email=email).exists():
            content['mensaje'] = "Correo en uso."
            return render(request, 'users/register.html', content)
        remoteUser = check_user(username, email)
        if remoteUser['state']:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            new_user = authenticate(request, username=user.username, password=password)
            profile = Profile.objects.get(usuario=user)
            if config('NOMBRE_SERVIDOR') == 'core_ONLINE':
                profile.subnet = request.POST['subnet']
            else:
                profile.subnet = config('NOMBRE_SERVIDOR')
            profile.save()
            UpdateThreadUsuario({'usuario':user.username, 'email': user.email, 'password': password, 'subnet': profile.subnet}).start()
            login(request, new_user)
            return redirect('web:index')
        else:
            content['mensaje'] = remoteUser['message']
            return render(request, 'users/register.html', content)                          
    else:
        return render(request, 'users/register.html')
    
def salir(request):
    logout(request)
    return redirect('web:index')

def pullUser(request, user):
    content = {'icon': 'error', 'user': user}
    if request.method == 'POST':
        password = request.POST['password']
        information = actualizacion_remota('get_user_info', {'usuario': user, 'password': password})
        if not information['estado']:
            content['mensaje'] = information['mensaje']
            return render(request, 'users/pullUser.html', content)
        new_user = User(username=information['username'], email=information['email'])
        new_user.set_password(password)
        new_user.save()
        profile = Profile.objects.get(usuario=new_user)
        profile.coins = information['coins']
        profile.sync - True
        profile.save()
        services = EstadoServicio.objects.get(usuario=new_user)
        services.internet  = information['internet']                               
        services.int_horas = information['int_horas']
        if information['int_time'] != 'None':
            services.int_time = information['int_time']
        services.int_tipo = information['int_tipo']
        services.int_duracion = information['int_duracion']
        services.int_velocidad = information['int_velocidad']
        services.int_auto = information['int_auto']
        services.jc = information['jc']
        if information['jc_time'] != 'None':
            services.jc_time = information['jc_time']
        services.jc_auto = information['jc_auto']
        services.emby = information['emby']
        services.emby_id = information['emby_id']
        if information['emby_time'] != 'None':
            services.emby_time = information['emby_time']
        services.emby_auto = information['emby_auto']
        services.ftp = information['ftp']
        services.ftp_auto = information['ftp_auto']
        if information['ftp_time'] != 'None':
            services.ftp_time = information['ftp_time']
        services.sync = True
        services.save()
        content['icon'] = 'success'
        content['mensaje'] = "Ya puede entrar con su usuario"
        return render(request, 'users/login.html', content)
    return render(request, 'users/pullUser.html', content)