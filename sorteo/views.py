from sorteo.actions import participacion
from django.contrib.auth.models import User
from .models import SorteoDetalle
from django.utils import timezone
from .forms import CodeForm
from django.shortcuts import render
from users.models import Notificacion


def index(request):
    form = CodeForm()
    content = {'notificaciones': False, 'form': form}
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            resultado = participacion(code)
            if resultado['estado']:
                content['success'] = 'success'
            print(resultado)
            content['message'] = resultado['mensaje']
            return render(request, 'sorteo/index.html', content)
        else:
            content['message'] = form.errors
            return render(request, 'sorteo/index.html', content)
    else:
        return render(request, 'sorteo/index.html', content)

def running(request):
    if User.objects.filter(username=request.user).exists():  
        usuario = User.objects.get(username=request.user)    
    else:         
        usuario = 'anonymous'
    mesActual = timezone.now().month
    if SorteoDetalle.objects.filter(mes=mesActual).exists():
        actual = SorteoDetalle.objects.get(mes=mesActual)
        activo = actual.activo
        finalizado = actual.finalizado
    else:
        actual = SorteoDetalle(mes=mesActual)
        actual.save()
        activo = actual.activo
        finalizado = actual.finalizado
    content = {
        'notificaciones': False,
        'usuario': usuario,
        'activo': activo,
        'finalizado': finalizado           
    }
    if request.user.is_authenticated:
        content['notificaciones'] = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
        content['notificaciones_nuevas'] = Notificacion.objects.filter(usuario=request.user, vista=False).order_by('-fecha')
    return render(request, 'sorteo/running.html', content)
