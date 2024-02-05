from django.shortcuts import render, redirect
from sync.syncs import actualizacion_remota
from django.contrib.auth.decorators import login_required
from decouple import config
from servicios.api.serializers import ServiciosSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from servicios.models import EstadoServicio, Recarga, Oper
from users.models import Profile, Notificacion
from sorteo.models import Sorteo, SorteoDetalle
from .models import MonthIncome, Spent
from . import actions
import datetime

import time

@login_required(login_url='/users/login/')
def control(request):    
    content = {}
    if request.method == 'POST':
        username = request.POST['usuario']
        busqueda = User.objects.filter(username__icontains=username)
        if len(busqueda) == 0:
            content["nulo"] = f"No se encontró nada relacionado con " + username     
        content['usuarios'] = busqueda
    return render(request, 'control/index.html', content)

@login_required(login_url='/users/login/')
def detalles(request, id):
    usuario = User.objects.get(id=id)
    opers = Oper.objects.filter(usuario=usuario).order_by('-fecha')
    content = {"usuario": usuario, "opers": opers}
    return render(request, 'control/detalle_usuario.html', content)

@login_required(login_url='/users/login/')
def funcion(request, id, funcion):
    usuario = User.objects.get(id=id)
    opers = Oper.objects.filter(usuario=usuario)
    content = {"usuario": usuario, "opers": opers}
    if funcion == "des_internet":
        servicio = EstadoServicio.objects.get(usuario=usuario)
        servicio.internet = False
        servicio.int_time = None
        servicio.int_horas = None
        servicio.int_auto = False        
        content['mensaje'] = "Internet desactivado con éxito."    
    if funcion == "des_emby":
        servicio = EstadoServicio.objects.get(usuario=usuario)
        servicio.emby = False
        servicio.emby_time = None
        servicio.emby_auto = False        
        content['mensaje'] = "Emby desactivado con éxito."
    content['icon'] = 'success'
    servicio.sync = False
    servicio.save()       
    return render(request, 'control/detalle_usuario.html', content)

@login_required(login_url='/users/login/')
def control_usuarios(request):
    usuarios = User.objects.all()
    content = {'usuarios': usuarios}
    return render(request, 'control/control_usuarios.html', content)

@login_required(login_url='/users/login/')
def control_perfiles(request):
    perfiles = Profile.objects.all()
    content = {'perfiles': perfiles}
    return render(request, 'control/control_perfiles.html', content)

@login_required(login_url='/users/login/')
def control_servicios(request):
    servicios = EstadoServicio.objects.all()
    content = {'servicios': servicios}
    return render(request, 'control/control_servicios.html', content)

@login_required(login_url='/users/login/')
def control_usuario(request, id):
    usuarios = User.objects.all()
    content = {'usuarios': usuarios}
    if request.method == 'POST':
        usuario = User.objects.get(id=id)       
        data = {'usuario': usuario.username} 
        respuesta = actualizacion_remota('check_usuario', data) 
        mensaje = respuesta['mensaje']       
        if respuesta['estado']:
            content['mensaje'] = respuesta['mensaje']
            return render(request, 'control/control_usuarios.html', content)
        else:
            mensaje = respuesta['mensaje']
            content = {'usuario': usuario.username, 'mensaje': mensaje, 'id': id}
            return render(request, 'control/crear_eliminar_usuario.html', content)       
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'control/control_usuarios.html', content)
    
@login_required(login_url='/users/login/')
def crear_eliminar_usuario(request, id):
    usuario = User.objects.get(id=id)
    usuarios = User.objects.all()
    content = {'usuarios': usuarios}
    if request.method == 'POST':
        if request.POST['respuesta'] == 'crear':
            data = {'usuario': usuario.username, 'email': usuario.email, 'password': usuario.password}
            resultado = actualizacion_remota('nuevo_usuario', data)
            content['mensaje'] = resultado['mensaje']
            return render(request, 'control/control_usuarios.html', content)            
        elif request.POST['respuesta'] == 'eliminar':
            usuario.delete()
            content['mensaje'] = "Se eliminó definitivamente el usuario."
            return render(request, 'control/control_usuarios.html', content)
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'control/control_usuarios.html', content)

@login_required(login_url='/users/login/')
def control_perfil(request, id):
    perfiles = Profile.objects.all()
    content = {'perfiles': perfiles,}
    if request.method == 'POST':
        usuario = User.objects.get(id=id)   
        profile = Profile.objects.get(usuario=usuario)
        data = {'usuario': usuario.username, 'coins': profile.coins}
        respuesta = actualizacion_remota('check_perfil', data)        
        if respuesta['estado']: 
            profile.sync = True
            profile.save()
            content['perfiles'] = Profile.objects.all()
            content['mensaje'] = respuesta['mensaje']
            return render(request, 'control/control_perfiles.html', content)
        else:
            mensaje = respuesta['mensaje']
            content = {'usuario': usuario.username, 'mensaje': mensaje, 'id': id}
            return render(request, 'control/actualizar_perfil.html', content)
        
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'control/control_perfiles.html', content)

@login_required(login_url='/users/login/')
def actualizar_perfil(request, id):
    usuario = User.objects.get(id=id)
    perfiles = Profile.objects.all()
    content = {'perfiles': perfiles}
    if request.method == 'POST':
        profile = Profile.objects.get(usuario=usuario)
        if request.POST['respuesta'] == 'local':
            data = {'usuario': usuario.username, 'coins': profile.coins}
            respuesta = actualizacion_remota('cambio_perfil', data)            
            if respuesta['estado']:
                content['perfiles'] = Profile.objects.all()    
            content['mensaje'] = respuesta['mensaje']
            return render(request, 'control/control_perfiles.html', content)            
        elif request.POST['respuesta'] == 'remoto':
            data = {'usuario': usuario.username}
            respuesta = actualizacion_remota('coger_perfil', data)
            if respuesta['estado']:
                profile.coins = respuesta['coins']
                profile.sync = True
                profile.save()
                content['perfiles'] = Profile.objects.all()      
            content['mensaje'] = respuesta['mensaje']
            return render(request, 'control/control_perfiles.html', content)
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'control/control_perfiles.html', content)

@login_required(login_url='/users/login/')
def control_servicio(request, id):
    usuario = User.objects.get(id=id)
    servicios = EstadoServicio.objects.all()
    servicio = EstadoServicio.objects.get(usuario=usuario)
    content = {'servicios': servicios}
    if request.method == 'POST':                   
        serializer = ServiciosSerializer(servicio)
        data=serializer.data
        data['usuario'] = usuario.username
        respuesta = actualizacion_remota('check_servicio', data)
        mensaje = respuesta['mensaje']
        if respuesta['conexion'] and not respuesta['estado']:
            content = {'usuario': usuario.username, 'id': id, 'mensaje': mensaje}
            return render(request, 'control/actualizar_servicio.html', content)
        servicio.sync = True
        servicio.save()
        content['servicios'] = EstadoServicio.objects.all()
        content['mensaje'] = mensaje
        return render(request, 'control/control_servicios.html', content)
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'control/control_servicios.html', content)

@login_required(login_url='/users/login/')
def actualizar_servicio(request, id):
    usuario = User.objects.get(id=id)
    servicios = EstadoServicio.objects.all()
    content = {'servicios': servicios}
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
                content['servicios'] = EstadoServicio.objects.all()
            content['mensaje'] = respuesta['mensaje']
            return render(request, 'control/control_servicios.html', content)
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
            content['mensaje'] = respuesta['mensaje']
            return render(request, 'control/index.html', content)
    else:
        content['mensaje'] = "Aqui no hay GET."
        return render(request, 'control/index.html', content)

@login_required(login_url='/users/login/')
def control_recargas(request):
    if request.method == 'POST':
        if request.POST.get('code'):
            code = request.POST['code']
            if Recarga.objects.filter(code=code).exists():
                recarga = Recarga.objects.get(code=code)
                content = {'recarga': recarga}
                return render(request, 'control/control_recargas.html', content)
            else:            
                data = {'usuario': str(request.user), 'check': True, 'code': code}
                respuesta = actualizacion_remota('usar_recarga', data)
                if respuesta['estado']:
                    recarga = {'mensaje': respuesta['mensaje'], 'code': respuesta['code'], 'cantidad': respuesta['cantidad'], 'activa': respuesta['activa'], 'usuario': respuesta['usuario'], 'fecha': respuesta['fecha'], 'icon': 'success'}
                    return render(request, 'control/control_recargas.html', recarga)
                else:
                    mensaje = respuesta['mensaje']
                    content = {'mensaje': mensaje}
                    return render(request, 'control/control_recargas.html', content)
        elif request.POST.get('numero'):
            numero = request.POST['numero']
            cantidad = request.POST['cantidad']
            recargas = []
            for _ in range(int(numero)):
                recarga = Recarga(cantidad=cantidad)      
                recargas.append(recarga)     
                recarga.save()      
            mensaje = 'Recargas guardadas'
            content = {'recargas': recargas, 'mensaje': mensaje, 'icon': 'success'}
            return render(request, 'control/control_recargas.html', content)
        else:
            mensaje = 'Algo salio mal con el POST'
            content = {'mensaje': mensaje}
            return render(request, 'control/control_recargas.html', content)
    else:
        return render(request, 'control/control_recargas.html')

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
    return render(request, 'control/control_sorteo.html', content)

@login_required(login_url='/users/login/')
def control_avanzado(request):
    if request.method == 'POST':
        if request.POST.get('chequeo'):
            chequeo = request.POST['chequeo']
            if chequeo == 'medula':
                data = {'identidad': 'local de iVan'}
                respuesta = actualizacion_remota('saludo', data)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
            elif chequeo == 'usuarios':
                usuarios = User.objects.all()
                for u in usuarios:
                    data = {'usuario': u.username}
                    respuesta = actualizacion_remota('check_usuario', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'control/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
            elif chequeo == 'perfiles':
                perfiles = Profile.objects.all()
                for p in perfiles:
                    data = {'usuario': p.usuario.username, 'coins': p.coins}
                    respuesta = actualizacion_remota('check_perfil', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'control/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
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
                        return render(request, 'control/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
            else:
                content = {'mensaje': 'Seleccione algo'}
                return render(request, 'control/control_avanzado.html', content)
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
                                return render(request, 'control/control_avanzado.html', content)
                        content = {'mensaje': mensaje}
                        return render(request, 'control/control_avanzado.html', content)                    
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
            elif accion == 'subir_perfiles':
                perfiles = Profile.objects.all()
                for p in perfiles:
                    data = {'usuario': p.usuario.username, 'coins': p.coins}
                    respuesta = actualizacion_remota('cambio_perfil', data)
                    if respuesta['estado'] == False:
                        mensaje = respuesta['mensaje']
                        content = {'mensaje': mensaje}
                        return render(request, 'control/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
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
                        return render(request, 'control/control_avanzado.html', content)
                mensaje = respuesta['mensaje']
                content = {'mensaje': mensaje}
                return render(request, 'control/control_avanzado.html', content)
            else:
                content = {'mensaje': 'Seleccione algo'}
                return render(request, 'control/control_avanzado.html', content)
    else:
        return render(request, 'control/control_avanzado.html')

def control_finanzas(request):
    month = timezone.now().month
    year = timezone.now().year
    day = timezone.now().day
    monthIncome = actions.get_or_create_monthincome(year, month)
    monthIncome.gross_income = actions.get_gross_income(year, month, monthIncome.days)
    monthIncome.total_spent = actions.get_total_spent(year, month)
    monthIncome.income = monthIncome.gross_income - monthIncome.total_spent
    monthIncome.save()
    spents = Spent.objects.filter(month=monthIncome)
    months = MonthIncome.objects.all()
    content = {'monthIncome': monthIncome, 'day': day, 'months': months, 'spents': spents}
    return render(request, 'control/control_finanzas.html', content)
    
def finanza_detalles(request, id):
    monthIncome = MonthIncome.objects.get(id=id)
    if request.method == 'POST':
        service = request.POST['service']
    else:
        service = 'internet-24h'
    pays = actions.get_service_pays(monthIncome.year, int(monthIncome.month), monthIncome.days, service)
    income = actions.get_service_income(pays)
    spents = actions.get_service_spents(monthIncome.year, int(monthIncome.month), service)
    spent = actions.get_service_spent(spents)
    content = {'monthIncome': monthIncome, 'service': service, 'pays': pays, 'income': income, 'spents': spents, 'spent': spent}
    return render(request, 'control/detalle_finanzas.html', content)

def crear_gasto(request):
    content = {'icon': 'error'}  
    if request.method == 'POST':
        if request.POST['nota'] == '' and request.POST['servicio'] == 'Selecciona si pertenece a un servicio':
            content['mensaje'] = 'Seleccione un servicio o una nota'
            return render(request, 'control/gasto_form.html', content)
        else:
            month = timezone.now().month
            year = timezone.now().year
            monthIncome = MonthIncome.objects.get(year=year, month=month)
            gasto = request.POST['cantidad']
            new_spent = Spent(month=monthIncome, spent=gasto)
            if request.POST.get('nota'):
                nota = request.POST['nota']
                new_spent.note = nota
            if request.POST['servicio'] != 'Selecciona si pertenece a un servicio':
                servicio = request.POST['servicio']
                new_spent.service = servicio
            new_spent.save()
            content['mensaje'] = 'Gasto guardado'
            content['icon'] = 'success'
            content['day'] = timezone.now().day
            content['spents'] = Spent.objects.filter(month=monthIncome)
            content['months'] = MonthIncome.objects.all()
            content['monthIncome'] = monthIncome
            return render(request, 'control/control_finanzas.html', content)
    return render(request, 'control/gasto_form.html')

def cerrar_mes(request):
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('cerrar'):
            month = timezone.now().month
            year = timezone.now().year
            monthIncome = MonthIncome.objects.get(year=year, month=month)
            monthIncome.closed = False
            monthIncome.save()
            return redirect('control:control_finanzas')
        else:
            return redirect('control:control_finanzas')
    return render(request, 'control/cerrar_mes.html')