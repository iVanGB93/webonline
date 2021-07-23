from django.shortcuts import render
from users.models import Notificacion


def index(request):
    content = {'notificaciones': False}
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    return render(request, 'web/index.html', content)

def ts(request):
    content = {'notificaciones': False}
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    return render(request, 'web/ts.html', content)

def ftp(request):
    content = {'notificaciones': False}
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    return render(request, 'web/ftp.html', content)

def emby(request):
    content = {'notificaciones': False}
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    return render(request, 'web/emby.html', content)

def jc(request):
    content = {'notificaciones': False}
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    return render(request, 'web/jc.html', content)
