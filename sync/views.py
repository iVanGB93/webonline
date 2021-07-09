from django.shortcuts import render
from .syncs import actualizacion_remota
from django.contrib.auth.decorators import login_required
from decouple import config
from servicios.api.serializers import ServiciosSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from servicios.models import EstadoServicio, Recarga
from users.models import Profile
from sorteo.models import Sorteo, SorteoDetalle

@login_required(login_url='/users/login/')
def control(request):
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    if request.method == 'POST':
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios}
        return render(request, 'sync/index.html', content)
    else:
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios}
        return render(request, 'sync/index.html', content)

@login_required(login_url='/users/login/')
def control_usuario(request, id):
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    if request.method == 'POST':
        usuario = User.objects.get(id=id)       
        data = {'usuario': usuario.username} 
        respuesta = actualizacion_remota('check_usuario', data) 
        mensaje = respuesta['mensaje']       
        if respuesta['estado']:
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)
        else:
            content = {'usuario': usuario.username, 'mensaje': mensaje, 'id': id}
            return render(request, 'sync/crear_eliminar_usuario.html', content)       
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)
    
@login_required(login_url='/users/login/')
def crear_eliminar_usuario(request, id):
    usuario = User.objects.get(id=id)
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    if request.method == 'POST':
        if request.POST['respuesta'] == 'crear':
            data = {'usuario': usuario.username, 'email': usuario.email, 'password': usuario.password}
            resultado = actualizacion_remota('nuevo_usuario', data)
            mensaje = resultado['mensaje']
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)            
        elif request.POST['respuesta'] == 'eliminar':
            usuario.delete()
            mensaje = "Se eliminó definitivamente el usuario."
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)

@login_required(login_url='/users/login/')
def control_perfil(request, id):
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    if request.method == 'POST':
        usuario = User.objects.get(id=id)   
        profile = Profile.objects.get(usuario=usuario)
        data = {'usuario': usuario.username, 'coins': profile.coins}
        respuesta = actualizacion_remota('check_perfil', data)        
        if respuesta['estado']: 
            profile.sync = True
            profile.save()
            perfiles = Profile.objects.all()
            mensaje = respuesta['mensaje']
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)
        else:
            mensaje = respuesta['mensaje']
            content = {'usuario': usuario.username, 'mensaje': mensaje, 'id': id}
            return render(request, 'sync/actualizar_perfil.html', content)
        
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)

@login_required(login_url='/users/login/')
def actualizar_perfil(request, id):
    usuario = User.objects.get(id=id)
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    if request.method == 'POST':
        profile = Profile.objects.get(usuario=usuario)
        if request.POST['respuesta'] == 'local':
            data = {'usuario': usuario.username, 'coins': profile.coins}
            respuesta = actualizacion_remota('cambio_perfil', data)            
            if respuesta['estado']:
                perfiles = Profile.objects.all()      
            mensaje = respuesta['mensaje']
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)            
        elif request.POST['respuesta'] == 'remoto':
            data = {'usuario': usuario.username}
            respuesta = actualizacion_remota('coger_perfil', data)
            if respuesta['estado']:
                profile.coins = respuesta['coins']
                profile.sync = True
                profile.save()
                perfiles = Profile.objects.all()      
            mensaje = respuesta['mensaje']
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)

@login_required(login_url='/users/login/')
def control_servicio(request, id):
    usuario = User.objects.get(id=id)
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    servicio = EstadoServicio.objects.get(usuario=usuario)
    if request.method == 'POST':                   
        serializer = ServiciosSerializer(servicio)
        data=serializer.data
        data['usuario'] = usuario.username
        respuesta = actualizacion_remota('check_servicio', data)
        mensaje = respuesta['mensaje']
        if respuesta['conexion'] and not respuesta['estado']:
            content = {'usuario': usuario.username, 'id': id, 'mensaje': mensaje}
            return render(request, 'sync/actualizar_servicio.html', content)
        servicio.sync = True
        servicio.save()
        servicios = EstadoServicio.objects.all()
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)

@login_required(login_url='/users/login/')
def actualizar_servicio(request, id):
    usuario = User.objects.get(id=id)
    usuarios = User.objects.all()
    perfiles = Profile.objects.all()
    servicios = EstadoServicio.objects.all()
    if request.method == 'POST':
        servicio = EstadoServicio.objects.get(usuario=usuario)
        if request.POST['respuesta'] == 'local':
            serializer = ServiciosSerializer(servicio)
            data=serializer.data
            data['usuario'] = usuario.username
            data['int_time'] = data['int_time']
            data['jc_time'] = data['jc_time']
            data['emby_time'] = data['emby_time']
            data['ftp_time'] = data['ftp_time']
            respuesta = actualizacion_remota('cambio_servicio', data)            
            if respuesta['estado']:
                servicio.sync = True
                servicio.save()
                servicios = EstadoServicio.objects.all()
            mensaje = respuesta['mensaje']
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)
        elif request.POST['respuesta'] == 'remoto':
            data = {'usuario': usuario.username}
            respuesta = actualizacion_remota('coger_servicios', data)
            if respuesta['estado']:
                servicio.internet = respuesta['internet']                               
                servicio.int_horas = respuesta['int_horas']
                if respuesta.get('int_time') == 'None':
                    servicio.int_time = None
                servicio.int_tipo = respuesta['int_tipo']
                servicio.int_auto = respuesta['int_auto']                  
                servicio.jc = respuesta['jc']
                if respuesta.get('jc_time') == 'None':
                    servicio.jc_time = None
                servicio.jc_auto = respuesta['jc_auto']
                servicio.emby = respuesta['emby']
                servicio.emby_id = respuesta['emby_id']
                if respuesta.get('emby_time') == 'None':
                    servicio.emby_time = None
                servicio.emby_auto = respuesta['emby_auto']
                servicio.ftp = respuesta['ftp']
                servicio.ftp_auto = respuesta['ftp_auto']
                if respuesta.get('ftp_time') == 'None':
                    servicio.ftp_time = None
                servicio.sync = True
                servicio.save()
            mensaje = respuesta['mensaje']
            content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
            return render(request, 'sync/index.html', content)
    else:
        mensaje = "Aqui no hay GET."
        content = {'usuarios': usuarios, 'perfiles': perfiles, 'servicios': servicios, 'mensaje': mensaje}
        return render(request, 'sync/index.html', content)

@login_required(login_url='/users/login/')
def control_recargas(request):
    if request.method == 'POST':
        if request.POST.get('code'):
            code = request.POST['code']
            if Recarga.objects.filter(code=code).exists():
                recargas = Recarga.objects.filter(code=code)
                content = {'recarga': recargas}
                return render(request, 'sync/control_recargas.html', content)
            else:            
                data = {'usuario': str(request.user), 'check': True, 'code': code}
                respuesta = actualizacion_remota('usar_recarga', data)
                if respuesta['estado']:
                    recarga = {'mensaje': respuesta['mensaje'], 'code': respuesta['code'], 'cantidad': respuesta['cantidad'], 'activa': respuesta['activa'], 'usuario': respuesta['usuario'], 'fecha': respuesta['fecha']}
                    return render(request, 'sync/control_recargas.html', recarga)
                else:
                    mensaje = respuesta['mensaje']
                    content = {'mensaje': mensaje}
                    return render(request, 'sync/control_recargas.html', content)
        elif request.POST.get('numero'):
            numero = request.POST['numero']
            cantidad = request.POST['cantidad']
            recargas = []
            for _ in range(int(numero)):
                recarga = Recarga(cantidad=cantidad)      
                recargas.append(recarga)     
                recarga.save()      
            mensaje = 'Recargas guardadas'
            content = {'recargas': recargas, 'mensaje': mensaje}
            return render(request, 'sync/control_recargas.html', content)
        else:
            mensaje = 'Algo salio mal con el POST'
            content = {'mensaje': mensaje}
            return render(request, 'sync/control_recargas.html', content)
    else:
        return render(request, 'sync/control_recargas.html')

@login_required(login_url='/users/login/')
def control_sorteos(request):
    mesActual = timezone.now().month
    if SorteoDetalle.objects.filter(mes=mesActual).exists():
        sorteo = SorteoDetalle.objects.get(mes=mesActual)
    else:
        sorteo = 'nada'
    content = {'sorteo': sorteo}
    if request.method == 'POST':
        accion = request.POST['accion']
        if accion == 'reiniciar':
            participantes = Sorteo.objects.filter(mes=mesActual)
            for p in participantes:
                p.eliminado = False
                p.save()
            sorteo.activo = False
            sorteo.finalizado = False
            sorteo.ganador = None
            sorteo.recarga = None
            sorteo.save()
    return render(request, 'sync/control_sorteo.html', content)

@login_required(login_url='/users/login/')
def control_avanzado(request):
    if request.method == 'POST':
        if request.POST.get('chequeo'):
            chequeo = request.POST['chequeo']
            if chequeo == 'medula':
                data = {'identidad': 'primera celula'}
                respuesta = actualizacion_remota('saludo', data)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            elif chequeo == 'usuarios':
                usuarios = User.objects.all()
                for u in usuarios:
                    data = {'usuario': u.username}
                    respuesta = actualizacion_remota('check_usuario', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'sync/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            elif chequeo == 'perfiles':
                perfiles = Profile.objects.all()
                for p in perfiles:
                    data = {'usuario': p.usuario.username, 'coins': p.coins}
                    respuesta = actualizacion_remota('check_perfil', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'sync/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            elif chequeo == 'servicios':
                servicios = EstadoServicio.objects.all()
                for s in servicios:
                    serializer = ServiciosSerializer(s)
                    data=serializer.data
                    data['usuario'] = s.usuario.username
                    respuesta = actualizacion_remota('check_servicio', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'sync/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            else:
                content = {'mensaje': 'Seleccione algo'}
                return render(request, 'sync/control_avanzado.html', content)
        if request.POST.get('accion'):
            accion = request.POST['accion']
            if accion == 'subir_usuarios':
                usuarios = User.objects.all()
                for u in usuarios:
                    data = {'usuario': u.username, 'email': u.email, 'first_name': u.first_name, 'last_name': u.last_name}
                    respuesta = actualizacion_remota('cambio_usuario', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        if mensaje == f'El usuario { u.username } no existe.':
                            data = {'usuario': u.username, 'email': u.email, 'password': u.username }
                            respuesta = actualizacion_remota('nuevo_usuario', data)
                            if respuesta['estado'] == False:
                                mensaje = respuesta['mensaje']
                                content = {'mensaje': mensaje}
                                return render(request, 'sync/control_avanzado.html', content)
                        content = {'mensaje': mensaje}
                        return render(request, 'sync/control_avanzado.html', content)                    
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            elif accion == 'subir_perfiles':
                perfiles = Profile.objects.all()
                for p in perfiles:
                    data = {'usuario': p.usuario.username, 'coins': p.coins}
                    respuesta = actualizacion_remota('cambio_perfil', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'sync/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            elif accion == 'subir_servicios':
                servicios = EstadoServicio.objects.all()
                for s in servicios:
                    serializer = ServiciosSerializer(s)
                    data=serializer.data
                    data['usuario'] = s.usuario.username
                    respuesta = actualizacion_remota('cambio_servicio', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'sync/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'sync/control_avanzado.html', content)
            else:
                content = {'mensaje': 'Seleccione algo'}
                return render(request, 'sync/control_avanzado.html', content)
    else:
        return render(request, 'sync/control_avanzado.html')