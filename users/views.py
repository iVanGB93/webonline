from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from users.models import Profile
from sync.models import EstadoConexion
from sync.actions import UpdateThreadUsuario
from .actions import check_user


def entrar(request):
    if request.user.is_authenticated:
        return redirect ('web:index')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('web:index')
            else:
                content = {'mensaje': "Contraseña Incorrecta", 'icon': 'error'}
                return render(request, 'users/login.html', content)            
        else:
            #chequear los servidores locales         
            content = {'mensaje': "Usuario no existe", 'icon': 'error'}
            return render(request, 'users/login.html', content)
    else:
        return render(request, 'users/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect ('web:index')
    content = {'icon': 'error'}
    if request.method == 'POST':
        conexion = EstadoConexion.objects.get(servidor='local_iVan')
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
        email2 = request.POST['emailConfirm']
        email = request.POST['email']
        if email != email2:
            content['mensaje'] = "Los correos no coinciden."
            return render(request, 'users/register.html', content)
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
            profile.subnet = request.POST['subnet']
            profile.save()
            UpdateThreadUsuario({'usuario':user.username, 'email': user.email, 'password': password}).start()
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