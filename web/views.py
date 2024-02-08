from django.shortcuts import render
from decouple import config


server_name = config('NOMBRE_SERVIDOR')

def index(request):
    content = {'local': False}
    if server_name != 'core_ONLINE':
        content['local'] = True
    return render(request, 'web/index.html', content)

def ts(request):
    content = {'local': False}
    if server_name != 'core_ONLINE':
        content['local'] = True
    return render(request, 'web/ts.html', content)

def ftp(request):
    content = {'local': False}
    if server_name != 'core_ONLINE':
        content['local'] = True
    return render(request, 'web/ftp.html')

def emby(request):
    content = {'local': False}
    if server_name != 'core_ONLINE':
        content['local'] = True
    return render(request, 'web/emby.html', content)

def jc(request):
    content = {'local': False}
    if server_name != 'core_ONLINE':
        content['local'] = True
    return render(request, 'web/jc.html')

def axie(request):
    content = {'local': False}
    if server_name != 'core_ONLINE':
        content['local'] = True
    return render(request, 'web/axie.html')
