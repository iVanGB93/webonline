from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import Comentario, Encuesta, Publicacion
from users.models import Notificacion


def tema_color(tema):
    if tema == "Emby":
        color = "success"
    elif tema == "Noticia":
        color = "warning"
    elif tema == "QbaRed":
        color = "info"
    elif tema == "Internet":
        color = "light"
    elif tema == "JovenClub":
        color = "primary"
    else:
        color = "danger"
    return color

def color_tema(color):
    if color == "success":
        tema = "Emby"
    elif color == "warning":
        tema = "Noticia"
    elif color == "info":
        tema = "QbaRed"
    elif color == "light":
        tema = "Internet"
    elif color == "primary":
        tema = "JovenClub"
    else:
        tema = "FileZilla"
    return tema

def index(request, pk):
    publicaciones = Publicacion.objects.filter(tema=pk).order_by('-fecha')
    todas = Publicacion.objects.all().order_by('-fecha')[:20]
    color = tema_color(pk)
    tema = pk
    data = {'publicaciones': publicaciones, 'todas': todas, 'color': color, 'tema': tema}
    return render(request, 'forum/index.html', data)

def detalles(request, tema, pk):
    publicacion = Publicacion.objects.get(id=pk)
    encuesta = 'nada'
    color = tema_color(tema)
    voto = 'no'
    comentarios = 'no'
    if Encuesta.objects.filter(publicacion=publicacion).exists():
        encuesta = Encuesta.objects.get(publicacion=publicacion)
        if request.user in encuesta.voto1.all() or request.user in encuesta.voto2.all() or request.user in encuesta.voto3.all() or request.user in encuesta.voto4.all() or request.user in encuesta.voto5.all():
            if request.user in encuesta.voto1.all():
                voto = 'opcion1'
            elif request.user in encuesta.voto2.all():
                voto = 'opcion2'
            elif request.user in encuesta.voto3.all():
                voto = 'opcion3'
            elif request.user in encuesta.voto4.all():
                voto = 'opcion4'
            else:
                voto = 'opcion5'
    if Comentario.objects.filter(publicacion=publicacion).exists():
        comentarios = Comentario.objects.filter(publicacion=publicacion).all().order_by('-fecha')
    content = {'p': publicacion, 'voto': voto, 'encuesta': encuesta, 'comentarios': comentarios, 'color': color, 'tema': tema}
    if request.method == 'POST':  
        if request.POST.get('eliminar'):
            comentario = Comentario.objects.get(id=request.POST['eliminar'])
            comentario.delete()      
            comentarios = Comentario.objects.filter(publicacion=publicacion).all().order_by('-fecha')
            content['mensaje'] = 'Comentario eliminado con éxito.'        
            return render(request, 'forum/detalles.html', content)
        if request.POST.get('comentario'):
            comentario = Comentario(publicacion=publicacion, autor=request.user, contenido=request.POST['comentario'])
            comentario.save()
            comentarios = Comentario.objects.filter(publicacion=publicacion).all().order_by('-fecha')
            content['mensaje'] = 'Comentario agregado con éxito.'
            content['comentarios'] = comentarios
            return render(request, 'forum/detalles.html', content)
        if request.POST.get('opcion'):
            opcion = request.POST['opcion']      
            if voto != 'no':  
                content['mensaje'] = 'Ya usted votó.'        
                return render(request, 'forum/detalles.html', content)
            if opcion == 'opcion1':    
                encuesta.voto1.add(request.user)
            elif opcion == 'opcion2':    
                encuesta.voto2.add(request.user)
            elif opcion == 'opcion3':    
                encuesta.voto3.add(request.user)
            elif opcion == 'opcion4':    
                encuesta.voto4.add(request.user)
            else:    
                encuesta.voto5.add(request.user)
            encuesta.save()
            content['mensaje'] = 'Su voto a sido guardado, gracias por participar.'
            content['voto'] = opcion
            return render(request, 'forum/detalles.html', content)
        else:
            content['mensaje'] = 'Seleccione una opción.'        
            return render(request, 'forum/detalles.html', content)
    else:
        if request.user != publicacion.autor:
            publicacion.visitas = publicacion.visitas + 1
            publicacion.save()
        return render(request, 'forum/detalles.html', content)

@login_required(login_url='/users/login/')
def crear(request, tema):
    color = tema_color(tema)
    voto = 'no'
    comentarios = 'no'
    content = {'voto': voto, 'comentarios': comentarios, 'tema': tema, 'color': color}    
    if request.method == 'POST':      
        usuario = User.objects.get(username=request.user)
        tema = request.POST['tema']
        titulo = request.POST['titulo']
        if Publicacion.objects.filter(titulo=titulo).exists():
            mensaje = 'Existe una publicación con este título'
            content['mensaje'] =  mensaje
            return render(request, 'forum/crear.html', content)
        contenido = request.POST['contenido']       
        nueva = Publicacion(autor=usuario, tema=tema, titulo=titulo, contenido=contenido)        
        if request.POST.get('online'):
            nueva.online = True
        if request.FILES.get('imagen1'):
            nueva.imagen1 = request.FILES['imagen1']
        if request.FILES.get('imagen2'):
            nueva.imagen2 = request.FILES['imagen2']       
        if request.FILES.get('imagen3'):
            nueva.imagen3 = request.FILES['imagen3']   
        nueva.save()             
        content['encuesta'] = 'nada'
        if request.POST.get('encuesta'):
            opcion1 = request.POST['opcion1']
            opcion2 = request.POST['opcion2']
            if opcion1 == '' or opcion2 == '':
                mensaje = 'Debe escribir al menos las 2 primeras opciones.'
                content['mensaje'] = mensaje
                nueva.delete()
                return render(request, 'forum/crear.html', content)
            else:
                encuesta = Encuesta(publicacion=nueva, opcion1=opcion1, opcion2=opcion2)
                if request.POST['opcion3'] != '':
                    encuesta.opcion3 = request.POST['opcion3']
                if request.POST['opcion4'] != '':
                    encuesta.opcion4 = request.POST['opcion4']
                if request.POST['opcion5'] != '':
                    encuesta.opcion5 = request.POST['opcion5']
                encuesta.save()
                content['encuesta'] = encuesta
        nueva.save()
        dato = f"Publicación de { nueva.tema } guardada"
        notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido=dato)
        notificacion.save()
        mensaje = 'Artículo publicado con éxito'
        content['p'] = nueva
        content['mensaje'] = mensaje    
        return render(request, 'forum/detalles.html', content)
    else:
        return render(request, 'forum/crear.html', content)

@login_required(login_url='/users/login/')
def editar(request, tema, pk):
    usuario = User.objects.get(username=request.user)
    publicacion = Publicacion.objects.get(id=pk)
    color = tema_color(tema)
    encuesta = 'nada'
    if Encuesta.objects.filter(publicacion=publicacion).exists():
        encuesta = Encuesta.objects.get(publicacion=publicacion)
    content = {'p': publicacion, 'encuesta': encuesta, 'tema': tema, 'color': color}    
    if request.method == 'POST':
        tema = request.POST['tema']
        publicacion.tema = tema
        if request.POST['titulo'] != '':
            titulo = request.POST['titulo']
            if titulo != publicacion.titulo:
                if Publicacion.objects.filter(titulo=titulo).exists():
                    mensaje = 'Existe una publicación con este título'
                    content['mensaje'] =  mensaje
                    return render(request, 'forum/editar.html', content)
            publicacion.titulo = titulo
        if request.POST['contenido'] != '':
            publicacion.contenido = request.POST['contenido']
        if request.POST.get('online'):
            publicacion.online = True
        else:
            publicacion.online = False
        if request.FILES.get('imagen1'):
            publicacion.imagen1 = request.FILES['imagen1']
        if request.FILES.get('imagen2'):
            publicacion.imagen2 = request.FILES['imagen2']       
        if request.FILES.get('imagen3'):
            publicacion.imagen3 = request.FILES['imagen3']
        publicacion.fecha = timezone.now()
        publicacion.save()  
        if request.POST.get('encuesta'):
            opcion1 = request.POST['opcion1']
            opcion2 = request.POST['opcion2']
            if opcion1 == '' or opcion2 == '':
                mensaje = 'Debe escribir al menos las 2 primeras opciones.'
                content['mensaje'] = mensaje
                return render(request, 'forum/editar.html', content)
            else:
                encuesta = Encuesta(publicacion=publicacion, opcion1=opcion1, opcion2=opcion2)
                if request.POST['opcion3'] != '':
                    encuesta.opcion3 = request.POST['opcion3']
                if request.POST['opcion4'] != '':
                    encuesta.opcion4 = request.POST['opcion4']
                if request.POST['opcion5'] != '':
                    encuesta.opcion5 = request.POST['opcion5']
                encuesta.save()
        else:  
            if encuesta != 'nada':            
                encuesta.delete()
        dato = f"Publicación de { publicacion.tema } editada"
        notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido=dato)
        notificacion.save()
        mensaje = 'Publicación modificada con éxito'
        content = {'p': publicacion, 'tema': tema, 'color': color}
        content['mensaje'] =  mensaje    
        return redirect('forum:detalles', tema, pk)
    else:
        return render(request, 'forum/editar.html', content) 

@login_required(login_url='/users/login/')
def eliminar(request, tema, pk):
    usuario = User.objects.get(username=request.user)
    publicacion = Publicacion.objects.get(id=pk)
    color = tema_color(tema)
    content = {'p': publicacion, 'tema': tema, 'color': color}    
    if request.method == 'POST':
        dato = f"Publicación de { publicacion.tema } eliminada"
        notificacion = Notificacion(usuario=usuario, tipo="REGISTRO", contenido=dato)
        notificacion.save()
        publicacion.delete()
        publicaciones = Publicacion.objects.filter(tema=pk).order_by('-fecha')
        todas = Publicacion.objects.all().order_by('-fecha')[:20]
        data = {'publicaciones': publicaciones, 'todas': todas, 'color': color, 'tema': tema}
        return redirect('forum:index', tema)
    else:
        return render(request, 'forum/eliminar.html', content)

