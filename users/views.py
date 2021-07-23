from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from decouple import config
from .forms import LoginForm, RegisterForm
from sync.syncs import actualizacion_remota
from sync.models import EstadoConexion


def entrar(request):
    if request.user.is_authenticated:
        return redirect ('/')
    form = LoginForm()
    content = {'form': form}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():            
            form = LoginForm(request.POST)
            if form.is_valid():
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('web:index')
                else:
                    form = LoginForm()
                    error = "Contraseña Incorrecta"
                    content = {'error': error, 'form': form}
                    return render(request, 'users/login.html', content)
            else:
                error = form.errors
                form = LoginForm()
                content = {'error': error, 'form': form}
                return render(request, 'users/login.html', content)
        else:            
            content['error'] = "Usuario NO Existe"
            return render(request, 'users/login.html', content)
    else:        
        return render(request, 'users/login.html', content)

def register(request):
    if request.user.is_authenticated:
        return redirect ('/')
    form = RegisterForm()
    content = {'form': form}
    if request.method == 'POST':
        online = config('APP_MODE')
        if online == 'online':
            servidor = config('NOMBRE_SERVIDOR')
            conexion = EstadoConexion.objects.get(servidor=servidor)
            if not conexion.online:
                content['error'] = "Registro deshabilitado, intente más tarde."
                return render(request, 'users/register.html', content)
        password = request.POST['password']
        if len(password) <8:
            content['error'] = "Contraseña mínimo 8 caracteres."
            return render(request, 'users/register.html', content)
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            content['error'] = "Nombre de usuario en uso."
            return render(request, 'users/register.html', content)
        if online == 'online':
            respuesta = actualizacion_remota('check_usuario', {'usuario': username})
            if respuesta['estado']:
                content['error'] = respuesta['mensaje']
                return render(request, 'users/register.html', content)
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            content['error'] = "Correo en uso."
            return render(request, 'users/register.html', content)
        if online == 'online':
            respuesta = actualizacion_remota('check_email', {'email': email})
            if respuesta['estado']:
                content['error'] = respuesta['mensaje']
                return render(request, 'users/register.html', content)
        email2 = request.POST['email2']
        if email != email2:
            content['error'] = "Los correos no coinciden."
            return render(request, 'users/register.html', content)        
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)            
            user.set_password(password)
            user.save()
            new_user = authenticate(username=user.username, password=password)  
            respuesta =  actualizacion_remota('nuevo_usuario', {'usuario':user.username, 'email': user.email, 'password': password})
            if respuesta['estado']:
                login(request, new_user)
                return redirect('web:index')
            else:
                form = LoginForm()
                error = respuesta['mensaje']
                content = {'error': error, 'form': form}
                return render(request, 'users/login.html', content)
        else:
            error = form.errors
            form = RegisterForm()
            content = {'error': error, 'form': form}
            return render(request, 'users/register.html', content)                                      
    else:        
        return render(request, 'users/register.html', content)
    
def salir(request):
    logout(request)
    return redirect('/')