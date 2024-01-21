from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from decouple import config
from sync.syncs import actualizacion_remota
from sync.models import EstadoConexion
from sync.actions import UpdateThreadUsuario


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
            content = {'mensaje': "Usuario no existe", 'icon': 'error'}
            return render(request, 'users/login.html', content)
    else:
        return render(request, 'users/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect ('web:index')
    content = {'icon': 'error'}
    if request.method == 'POST':
        online = config('APP_MODE')
        if online == 'online':
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
        if online == 'online':
            check_user = actualizacion_remota('check_usuario', {'usuario': username})
            if check_user['conexion']:
                if check_user['estado']:
                    content['mensaje'] = check_user['mensaje']
                    return render(request, 'users/register.html', content)
            else:
                content['mensaje'] = "Registro deshabilitado, intente más tarde."
                return render(request, 'users/register.html', content)
            check_email = actualizacion_remota('check_email', {'email': email})
            if check_email['conexion']:
                if check_email['estado']:
                    content['mensaje'] = check_email['mensaje']
                    return render(request, 'users/register.html', content)
            else:
                content['mensaje'] = "Registro deshabilitado, intente más tarde."
                return render(request, 'users/register.html', content)
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        new_user = authenticate(request, username=user.username, password=password)        
        UpdateThreadUsuario({'usuario':user.username, 'email': user.email, 'password': password}).start()
        login(request, new_user)
        return redirect('web:index')                  
    else:        
        return render(request, 'users/register.html')
    
def salir(request):
    logout(request)
    return redirect('web:index')