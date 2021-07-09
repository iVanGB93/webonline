from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from decouple import config
from .forms import LoginForm, RegisterForm
from sync.syncs import actualizacion_remota


def entrar(request):
    if request.user.is_authenticated:
        return redirect ('/')
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
            form = LoginForm()
            error = "Usuario NO Existe"
            content = {'error': error, 'form': form}
            return render(request, 'users/login.html', content)
    else:
        form = LoginForm()
        content = {'form': form}
        return render(request, 'users/login.html', content)

def register(request):
    if request.user.is_authenticated:
        return redirect ('/')
    if request.method == 'POST':
        password = request.POST['password']
        if len(password) <8:
            form = RegisterForm()
            error = "Contraseña mínimo 8 caracteres."
            content = {'error': error, 'form': form}
            return render(request, 'users/register.html', content)
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            form = RegisterForm()
            error = "Nombre de usuario en uso."
            content = {'error': error, 'form': form}
            return render(request, 'users/register.html', content)
        if config('APP_MODE') == 'online':
            respuesta = actualizacion_remota('check_usuario', {'usuario': username})
            if respuesta['estado']:
                form = RegisterForm()
                error = respuesta['mensaje']
                content = {'error': error, 'form': form}
                return render(request, 'users/register.html', content)
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            form = RegisterForm()
            error = "Correo en uso."
            content = {'error': error, 'form': form}
            return render(request, 'users/register.html', content)
        if config('APP_MODE') == 'online':
            respuesta = actualizacion_remota('check_email', {'email': email})
            if respuesta['estado']:
                form = RegisterForm()
                error = respuesta['mensaje']
                content = {'error': error, 'form': form}
                return render(request, 'users/register.html', content)
        email2 = request.POST['email2']
        if email != email2:
            form = RegisterForm()
            error = "Los correos no coinciden."
            content = {'error': error, 'form': form}
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
        form = RegisterForm()
        content = {'form': form}
        return render(request, 'users/register.html', content)
    
def salir(request):
    logout(request)
    return redirect('/')