from django.shortcuts import render


def index(request):
    return render(request, 'web/index.html')

def ts(request):
    return render(request, 'web/ts.html')

def ftp(request):
    return render(request, 'web/ftp.html')

def emby(request):
    return render(request, 'web/emby.html')

def jc(request):
    return render(request, 'web/jc.html')
