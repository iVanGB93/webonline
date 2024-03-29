from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decouple import config
from users.models import Profile, Notificacion
from servicios.models import EstadoServicio, Oper
from sorteo.models import SorteoDetalle
from servicios.actions import *
from sync.syncs import actualizacion_remota

from servicios.api.serializers import ServiciosSerializer

@login_required(login_url='/users/login/')
def dashboard(request):
    sorteos = SorteoDetalle.objects.all()
    conexion = EstadoConexion.objects.get(id=1)
    content = {'conexion': conexion, 'sorteos': sorteos}
    return render(request, 'portal/dashboard.html', content)

@login_required(login_url='/users/login/')
def perfil(request):
    content = {'icon': 'error'}
    usuario = User.objects.get(username=request.user)
    conexion = EstadoConexion.objects.get(id=1)
    if request.method == 'POST':
        if request.FILES.get('imagen'):
            perfil = Profile.objects.get(usuario=usuario)
            perfil.imagen = request.FILES['imagen']
            perfil.save()
            notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido="Imagen de perfil cambiada")
            notificacion.save()
            content['mensaje'] = 'Imagen guardada con éxito.'
            content['icon'] = 'success'
            return render(request, 'portal/perfil.html', content)
        email = request.POST['email']   
        if User.objects.filter(email=email).exists():
            dueño = User.objects.get(email=email)
            if dueño.username != usuario.username:
                content['mensaje'] = "El correo está en uso."
                return render(request, 'portal/perfil.html', content)
        usuario.email = email
        usuario.first_name = request.POST['first_name']
        usuario.last_name = request.POST['last_name']
        if config('APP_MODE') == 'online':
            if conexion.online:
                respuesta = actualizacion_remota('check_email', {'email': email})
                if respuesta['estado']:
                    if User.objects.filter(email=email).exists():
                        dueño = User.objects.get(email=email)
                        if dueño.username != usuario.username:
                            content['mensaje'] = respuesta['mensaje']
                            return render(request, 'portal/perfil.html', content)                     
                    else:
                        content['mensaje'] = 'Usuario local no encontrado, notifique a la administración del error'
                        return render(request, 'portal/perfil.html', content)
                data = {'usuario': usuario.username, 'email': usuario.email, 'first_name': usuario.first_name, 'last_name': usuario.last_name}       
                respuesta = actualizacion_remota('cambio_usuario', data)          
                if not respuesta['estado']:                
                    content['mensaje'] = respuesta['mensaje']
                    return render(request, 'portal/perfil.html', content)  
            else:
                content['mensaje'] = 'No disponible en este momento, intente más tarde.'
                return render(request, 'portal/perfil.html', content)
        notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido="Detalles de perfil editados")
        notificacion.save()
        usuario.save()
        content['icon'] = 'success'
        content['mensaje'] = 'Perfil editado con éxito'
        return render(request, 'portal/perfil.html', content)
    else:
        return render(request, 'portal/perfil.html', content)

@login_required(login_url='/users/login/')
def contra(request):
    content = {'icon': 'error'}
    if request.method == 'POST':
        usuario = User.objects.get(username=request.user)
        contra = request.POST['actual']
        if usuario.check_password(contra):
            if request.POST['nueva'] == request.POST['confirme']:
                if len(request.POST['nueva']) >= 8:
                    nueva = request.POST['nueva']
                    conexion = EstadoConexion.objects.get(id=1)
                    if config('APP_MODE') == 'online':
                        if conexion.online:
                            data = {'usuario': usuario.username, 'contraseña': nueva}
                            respuesta = actualizacion_remota('nueva_contraseña', data)
                            if not respuesta['estado']:
                                content['mensaje'] = respuesta['mensaje']
                                return render(request, 'portal/cambiarcontra.html', content)
                    usuario.set_password(nueva)
                    notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido="Contraseña de usuario cambiada")
                    notificacion.save()
                    usuario.save()
                    content['icon'] = 'success'
                    content['mensaje'] = 'Contraseña cambiada con éxito.'
                    return render(request, 'portal/cambiarcontra.html', content)
                else:
                    content['mensaje'] = 'La contraseña debe tener al menos 8 caracteres.'
                    return render(request, 'portal/cambiarcontra.html', content)
            else:
                content['mensaje'] = 'Las contraseñas nuevas no coinciden.'
                return render(request, 'portal/cambiarcontra.html', content)
        else:
            content['mensaje'] = 'Contraseña actual incorrecta.'
            return render(request, 'portal/cambiarcontra.html', content)
    else:
        return render(request, 'portal/cambiarcontra.html', content)

@login_required(login_url='/users/login/')
def internet(request):
    usuario = request.user
    internetSemanalPrice = config('INTERNET_PRICE_SEMANAL')
    internetHorasPrice = config('INTERNET_PRICE_HORAS')
    content = {'icon': 'error',  'internetSemanalPrice': internetSemanalPrice, 'internetHorasPrice': internetHorasPrice} 
    if request.method == 'POST':
        tipo = request.POST['tipo']
        duracion = request.POST['duracion']
        velocidad = request.POST['velocidad']
        horas = request.POST['cantidad_horas']
        contra = request.POST['contra']        
        if usuario.check_password(contra):
            result = comprar_internet(usuario, tipo, contra, duracion, horas, velocidad)
            if result['correcto']:      
                content['icon'] = 'success'             
            content['mensaje'] = result['mensaje']
            return render(request, 'portal/internet.html', content)
        else:
            content['mensaje'] = 'Contraseña incorrecta.'
            return render(request, 'portal/internet.html', content)       
    else:
        return render(request, 'portal/internet.html', content)

@login_required(login_url='/users/login/')
def jovenclub(request):
    usuario = request.user
    jcPrice = config('JC_PRICE')
    content = {'icon': 'error', 'jcPrice': jcPrice} 
    if request.method == 'POST':
        contra = request.POST['contra']
        if usuario.check_password(contra):
            result = comprar_jc(usuario)
            if result['correcto']:                
                content['icon'] = 'success'                
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
    embyPrice = config('EMBY_PRICE')
    content = {'icon': 'error', 'embyPrice': embyPrice} 
    if request.method == 'POST':
        contra = request.POST['contra']
        if usuario.check_password(contra):
            result = comprar_emby(usuario)
            if result['correcto']:
                content['icon'] = 'success'
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
    ftpPrice = config('FTP_PRICE')
    content = {'icon': 'error', 'ftpPrice': ftpPrice}
    if request.method == 'POST':
        contra = request.POST['contra']        
        if usuario.check_password(contra):                    
            result = comprar_filezilla(usuario, contra)
            if result['correcto']:
                content['icon'] = 'success'
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
    content = {'icon': 'error'} 
    if request.method == 'POST':
        code = request.POST['code']                        
        result = recargar(code, usuario)
        if result['correcto']:
            content['icon'] = 'success'
        content['mensaje'] = result['mensaje']              
    return render(request, 'portal/recarga.html', content)

@login_required(login_url='/users/login/')
def transferencia(request):
    usuario = request.user
    content = {'icon': 'error'} 
    if request.method == 'POST':        
        hacia = request.POST['hacia']
        cantidad = request.POST['cantidad']     
        result = transferir(usuario, hacia, cantidad)
        if result['correcto']:
            content['icon'] = 'success'
        content['mensaje'] = result['mensaje']        
    return render(request, 'portal/transferencia.html', content)

@login_required(login_url='/users/login/')
def operaciones(request):
    usuario = request.user
    content = {'icon': 'error'} 
    if User.objects.filter(username=usuario).exists():
        opers = Oper.objects.filter(usuario=usuario).order_by('-fecha')[:10]
        content['opers'] = opers
        return render(request, 'portal/operaciones.html', content)
    else:
        content['mensaje'] = 'Usuario no existe'
        return render (request, 'portal/operaciones.html', content)

@login_required(login_url='/users/login/')
def cambiar_auto(request, id):
    usuario = request.user
    perfil = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=perfil.subnet)
    servicio = EstadoServicio.objects.get(usuario=usuario)
    content = {'servicio': servicio, 'icon': 'success'}
    if conexion.online:
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
    else:
        content['mensaje'] = "El servidor no tiene acceso a internet en este momento, intente más tarde."
        content['icon'] = 'error'
        return render(request, f'portal/{ id }.html', content)
    
@login_required(login_url='/users/login/')
def sync_servicio(request, id):
    usuario = request.user
    perfil = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=perfil.subnet)
    content = {'icon': 'error'}
    if conexion.online:
        servicio = EstadoServicio.objects.get(usuario=usuario)
        servicio.sync = False
        servicio.save()
        content['mensaje'] = 'Servicios actualizados, si continua el problema contacte un admin.'
        content['icon'] = 'success'
        return render(request, f'portal/{ id }.html', content)
    else:
        content['mensaje'] = "El servidor no tiene acceso a internet en este momento, intente más tarde."
        return render(request, f'portal/{ id }.html', content)
    
@login_required(login_url='/users/login/')
def guardar_servicio(request):
    usuario = request.user
    content = {'icon': 'error'}
    servicio = EstadoServicio.objects.get(usuario=usuario)
    serializer = ServiciosSerializer(servicio)
    data=serializer.data
    data['usuario'] = str(usuario)
    respuesta = actualizacion_remota('cambio_servicio', data)
    if respuesta['estado']:
        content['icon'] = 'success'
        servicio.sync = True
        servicio.save()
    content['mensaje'] = respuesta['mensaje']
    return render(request, 'portal/dashboard.html', content)

@login_required(login_url='/users/login/')
def sync_perfil(request):    
    usuario = request.user
    profile = Profile.objects.get(usuario=usuario)
    conexion = EstadoConexion.objects.get(servidor=profile.subnet)
    sorteos = SorteoDetalle.objects.all()
    content = {'sorteos': sorteos, 'conexion': conexion, 'icon': 'error'}
    if request.method == 'POST':
        if conexion.online:
            profile.sync = False
            profile.save()
            content['mensaje'] = 'Perfil actualizado, si continua el problema contacte un admin.'
            content['icon'] = 'success'
            return render(request, 'portal/dashboard.html', content)
        else:
            content['mensaje'] = "El servidor no tiene acceso a internet en este momento, intente más tarde."
            return render(request, 'portal/dashboard.html', content)
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'portal/dashboard.html', content)

@login_required(login_url='/users/login/')
def guardar_perfil(request):
    usuario = User.objects.get(username=request.user)
    perfil = Profile.objects.get(usuario=usuario)
    content = {'icon': 'error'}
    if request.method == 'POST':
        data = {'usuario': usuario.username, 'coins': perfil.coins}
        respuesta = actualizacion_remota('cambio_perfil', data)            
        if respuesta['estado']:
            content['icon'] = 'success'
            perfil.sync = True
            perfil.save()
        content['mensaje'] = respuesta['mensaje']
        return render(request, 'portal/dashboard.html', content)
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'portal/dashboard.html', content)