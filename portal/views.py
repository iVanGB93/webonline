from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decouple import config
from users.models import Profile
from .forms import EditUserForm
from servicios.models import EstadoServicio, Oper
from sorteo.models import SorteoDetalle
from servicios.actions import *
from sync.syncs import actualizacion_remota

from servicios.api.serializers import ServiciosSerializer

def index(request):
    return render(request, 'portal/index.html')

@login_required(login_url='/users/login/')
def dashboard(request):
    tiempo = timezone.now()
    sorteos = SorteoDetalle.objects.all()
    content = {'tiempo': tiempo, 'sorteos': sorteos}
    return render(request, 'portal/dashboard.html', content)

@login_required(login_url='/users/login/')
def perfil(request):
    usuario = User.objects.get(username=request.user)
    if request.method == 'POST':
        form = EditUserForm(request.POST)
        if form.is_valid():
            usuario.email = request.POST['email']
            usuario.first_name = request.POST['first_name']
            usuario.last_name = request.POST['last_name']
            if config('APP_MODE') == 'online':
                data = {'usuario': usuario.username, 'email': usuario.email, 'first_name': usuario.first_name, 'last_name': usuario.last_name}       
                respuesta = actualizacion_remota('cambio_usuario', data)          
                if respuesta['estado']:
                    usuario.save()
                form = EditUserForm()
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje, 'form': form}
                return render(request, 'portal/perfil.html', content)
            else:                
                usuario.save()
                form = EditUserForm()
                mensaje = 'Perfil editado con éxito'
                content = {'mensaje': mensaje, 'form': form}
                return render(request, 'portal/perfil.html', content)
        else:
            mensaje = form.errors
            form = EditUserForm()
            content = {'mensaje': mensaje, 'form': form}
            return render(request, 'portal/perfil.html', content)
    else:
        form = EditUserForm()
        content = {'form': form}
        return render(request, 'portal/perfil.html', content)

@login_required(login_url='/users/login/')
def contra(request):
    if request.method == 'POST':        
        usuario = User.objects.get(username=request.user)
        contra = request.POST['actual']
        if usuario.check_password(contra):
            if request.POST['nueva'] == request.POST['confirme']:
                if len(request.POST['nueva']) >= 8:
                    nueva = request.POST['nueva']
                    if config('APP_MODE') == 'online':
                        data = {'usuario': usuario.username, 'contraseña': nueva}
                        respuesta = actualizacion_remota('nueva_contraseña', data)
                        if respuesta['estado']:
                            usuario.set_password(nueva)
                            usuario.save()
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'portal/cambiarcontra.html', content)
                    else:
                        usuario.set_password(nueva)
                        usuario.save()
                        mensaje = 'Contraseña cambiada con éxito.'
                        content = {'mensaje': mensaje}
                        return render(request, 'portal/cambiarcontra.html', content)
                else:
                    mensaje = 'La contraseña debe tener al menos 8 caracteres.'
                    content = {'mensaje': mensaje}
                    return render(request, 'portal/cambiarcontra.html', content)
            else:
                mensaje = 'Las contraseñas nuevas no coinciden.'
                content = {'mensaje': mensaje}
                return render(request, 'portal/cambiarcontra.html', content)
        else:
            mensaje = 'Contraseña actual incorrecta.'
            content = {'mensaje': mensaje}
            return render(request, 'portal/cambiarcontra.html', content)
    else:
        return render(request, 'portal/cambiarcontra.html')

@login_required(login_url='/users/login/')
def internet(request):
    usuario = request.user
    content = {'color_msg': 'danger'} 
    if request.method == 'POST':
        tipo = request.POST['tipo']
        horas = request.POST['cantidad_horas']
        contra = request.POST['contra']
        if tipo != 'Seleccione el tipo':
            if usuario.check_password(contra):
                result = comprar_internet(usuario, tipo, contra, horas)
                if result['correcto']:                   
                    content['color_msg'] = 'success'
                content['mensaje'] = result['mensaje']
                return render(request, 'portal/internet.html', content)
            else:
                content['mensaje'] = 'Contraseña incorrecta.'
                return render(request, 'portal/internet.html', content)
        else:
            content['mensaje'] = 'Seleccione un tipo de internet'
            return render(request, 'portal/internet.html', content)         
    else:
        return render(request, 'portal/internet.html', content)

@login_required(login_url='/users/login/')
def jovenclub(request):
    usuario = request.user
    content = {'color_msg': 'danger'} 
    if request.method == 'POST':
        contra = request.POST['contra']
        if usuario.check_password(contra):
            result = comprar_jc(usuario)
            if result['correcto']:                
                content['color_msg'] = 'success'
            content['mensaje'] = result['mensaje']
            return render(request, 'portal/jovenclub.html', content)
        else:
            content['mensaje'] = 'Contraseña incorrecta.'
            return render(request, 'portal/jovenclub.html', content)
    else:
        return render(request, 'portal/jovenclub.html', content)

@login_required(login_url='/users/login/')
def emby(request):
    usuario = request.user
    content = {'color_msg': 'danger'} 
    if request.method == 'POST':
        contra = request.POST['contra']
        if usuario.check_password(contra):
            result = comprar_emby(usuario)
            if result['correcto']:                
                content['color_msg'] = 'success'
            content['mensaje'] = result['mensaje']
            return render(request, 'portal/emby.html', content)
        else:
            content['mensaje'] = 'Contraseña incorrecta.'
            return render(request, 'portal/emby.html', content)
    else:
        return render(request, 'portal/emby.html', content)

@login_required(login_url='/users/login/')
def filezilla(request):
    usuario = request.user
    content = {'color_msg': 'danger'} 
    if request.method == 'POST':
        contra = request.POST['contra']        
        if usuario.check_password(contra):                    
            result = comprar_filezilla(usuario, contra)
            if result['correcto']:
                content['color_msg'] = 'success'
            content['mensaje'] = result['mensaje']
            return render(request, 'portal/filezilla.html', content)
        else:
            content['mensaje'] = 'Contraseña incorrecta.'
            return render(request, 'portal/filezilla.html', content)
    else:
        return render(request, 'portal/filezilla.html', content)

@login_required(login_url='/users/login/')
def recarga(request):
    usuario = request.user
    perfil = Profile.objects.get(usuario=usuario)
    content = {'color_msg': 'danger'}
    if request.method == 'POST':
        code = request.POST['code']
        if len(code) != 8:
            content['mensaje'] = 'Escriba 8 digitos.'
            return render(request, 'portal/recarga.html', content)
        if not perfil.sync:
            content['mensaje'] = "Sincronice su perfil en dashboard para poder recargar."
            return render(request, 'portal/recarga.html', content)        
        result = recargar(code, usuario)
        if result['correcto']:
            content['color_msg'] = 'success'
            perfil = Profile.objects.get(usuario=usuario)
            content['perfil'] = perfil
        content['mensaje'] = result['mensaje']
        return render(request, 'portal/recarga.html', content)            
        
    else:     
        return render(request, 'portal/recarga.html', content)

@login_required(login_url='/users/login/')
def transferencia(request):
    usuario = request.user
    perfil = Profile.objects.get(usuario=usuario)
    content = {'color_msg': 'danger'}
    if request.method == 'POST':
        if not perfil.sync:
            content['mensaje'] = "Sincronice su perfil en dashboard para poder transferir"
            return render(request, 'portal/transferencia.html', content)
        hacia = request.POST['hacia']
        cantidad = request.POST['cantidad']     
        result = transferir(usuario, hacia, cantidad)
        if result['correcto']:
            content['color_msg'] = 'success'        
        content['mensaje'] = result['mensaje']
        return render(request, 'portal/transferencia.html', content)        
    else:
        return render(request, 'portal/transferencia.html', content)

@login_required(login_url='/users/login/')
def operaciones(request):
    usuario = request.user
    if User.objects.filter(username=usuario).exists():
        opers = Oper.objects.filter(usuario=usuario).order_by('-fecha')[:10]
        content = {'opers': opers}
        return render(request, 'portal/operaciones.html', content)
    else:
        mensaje = 'Usuario no existe'
        content = {'mensaje': mensaje}
        return render (request, 'portal/operaciones.html', content)

@login_required(login_url='/users/login/')
def cambiar_auto(request, id):
    usuario = request.user
    servicio = EstadoServicio.objects.get(usuario=usuario)
    content = {'servicio': servicio, 'color_msg': 'success'}
    if servicio.sync:
        if id == 'internet':
            if servicio.int_auto:
                servicio.int_auto = False
                servicio.sync = False
                servicio.save()
            else:
                servicio.int_auto = True
                servicio.sync = False
                servicio.save()
        elif id == 'jovenclub':
            if servicio.jc_auto:
                servicio.jc_auto = False
                servicio.sync = False
                servicio.save()
            else:
                servicio.jc_auto = True
                servicio.sync = False
                servicio.save()
        elif id == 'emby':
            if servicio.emby_auto:
                servicio.emby_auto = False
                servicio.sync = False
                servicio.save()
            else:
                servicio.emby_auto = True
                servicio.sync = False
                servicio.save()
        elif id == 'filezilla':
            if servicio.ftp_auto:
                servicio.ftp_auto = False
                servicio.sync = False
                servicio.save()
            else:
                servicio.ftp_auto = True
                servicio.sync = False
                servicio.save()
        else:
            content['mensaje'] = 'Ocurrio algún error'
            return render(request, f'portal/{ id }.html', content)
        content['mensaje'] = 'Activación automática cambiada con éxito'
        content['servicio'] = EstadoServicio.objects.get(usuario=usuario)
        return render(request, f'portal/{ id }.html', content)
    else:
        content['mensaje'] = 'Debe sincronizar sus servicios para realizar cambios.'
        return render(request, f'portal/{ id }.html', content)
    
@login_required(login_url='/users/login/')
def sync_servicio(request, id):
    usuario = request.user
    perfil = Profile.objects.get(usuario=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario)
    serializer = ServiciosSerializer(servicio)
    data=serializer.data
    data['usuario'] = str(usuario)    
    respuesta = actualizacion_remota('check_servicio', data)
    if respuesta['estado']:
        servicio.sync = True
        servicio.save()
        mensaje = respuesta['mensaje']
        content = {'mensaje': mensaje, 'perfil': perfil, 'servicio': servicio, 'color_msg': 'success'}
        return render(request, f'portal/{ id }.html', content)
    else:
        content = {'id': id}
        return render(request, 'portal/sync.html', content)
    
@login_required(login_url='/users/login/')
def guardar_servicio(request):
    usuario = request.user
    perfil = Profile.objects.get(usuario=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario)
    serializer = ServiciosSerializer(servicio)
    data=serializer.data
    data['usuario'] = str(usuario)
    respuesta = actualizacion_remota('cambio_servicio', data)
    if respuesta['estado']:
        servicio.sync = True
        servicio.save()
    mensaje = respuesta['mensaje']
    content = {'mensaje': mensaje, 'perfil': perfil, 'servicio': servicio}
    return render(request, f'portal/dashboard.html', content)

@login_required(login_url='/users/login/')
def sync_perfil(request):    
    usuario = User.objects.get(username=request.user)
    perfil = Profile.objects.get(usuario=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario)    
    if request.method == 'POST':
        profile = Profile.objects.get(usuario=usuario)        
        data = {'usuario': usuario.username, 'coins': profile.coins}
        respuesta = actualizacion_remota('check_perfil', data)        
        if respuesta['estado']:
            profile.sync = True
            profile.save()
            mensaje = respuesta['mensaje']
            content = {'usuario': usuario, 'perfil': perfil, 'servicio': servicio, 'mensaje': mensaje}
            return render(request, 'portal/dashboard.html', content)
        else:
            return render(request, 'portal/sync_perfil.html')
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuario': usuario, 'perfil': perfil, 'servicio': servicio, 'mensaje': mensaje}
        return render(request, 'portal/dashboard.html', content)

@login_required(login_url='/users/login/')
def guardar_perfil(request):
    usuario = User.objects.get(username=request.user)
    perfil = Profile.objects.get(usuario=usuario)
    servicio = EstadoServicio.objects.get(usuario=usuario)   
    if request.method == 'POST':
        data = {'usuario': usuario.username, 'coins': perfil.coins}
        respuesta = actualizacion_remota('cambio_perfil', data)            
        if respuesta['estado']:
            perfil.sync = True
            perfil.save()    
        mensaje = respuesta['mensaje']
        content = {'usuario': usuario, 'perfil': perfil, 'servicio': servicio, 'mensaje': mensaje}
        return render(request, 'portal/dashboard.html', content)
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuario': usuario, 'perfil': perfil, 'servicio': servicio, 'mensaje': mensaje}
        return render(request, 'portal/dashboard.html', content)