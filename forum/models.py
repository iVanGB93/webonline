from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.db import models

def upload_to(instance, filename):
    return 'forum/{filename}'.format(filename=filename)

class Publicacion(models.Model):
    opcionesTema = (
        ('Noticia', 'Noticia'),
        ('Internet', 'Internet'),
        ('JovenClub', 'JovenClub'),
        ('Emby', 'Emby'),
        ('FileZilla', 'FileZilla'),
        ('QbaRed', 'QbaRed'),
    )
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    tema = models.CharField(max_length=15, choices=opcionesTema)
    titulo = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60)
    contenido = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    sync= models.BooleanField(default=False)
    visitas = models.PositiveIntegerField(default=0)
    imagen1 = models.ImageField(_("Imagen1"), upload_to=upload_to, default='defaultForum.png')
    imagen2 = models.ImageField(_("Imagen2"), upload_to=upload_to, default='defaultForum.png')
    imagen3 = models.ImageField(_("Imagen3"), upload_to=upload_to, default='defaultForum.png')

    def __str__(self):
        return "Usuario: " + self.autor.username + " tema: " + self.tema +  " título: " + self.titulo
    
    def save(self, *args, **kwargs):
        value = self.titulo
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    contenido = models.TextField()

    def __str__(self):
        return "Comentario de " + self.autor.username + " en " + self.publicacion.titulo

class RespuestaComentario(models.Model):
    comentario = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    contenido = models.TextField()

class Encuesta(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    opcion1 = models.CharField(max_length=60)
    opcion2 = models.CharField(max_length=60)
    opcion3 = models.CharField(max_length=60)
    opcion4 = models.CharField(max_length=60)
    opcion5 = models.CharField(max_length=60)
    voto1 = models.ManyToManyField(User, related_name='Opcion1')
    voto2 = models.ManyToManyField(User, related_name='Opcion2')
    voto3 = models.ManyToManyField(User, related_name='Opcion3')
    voto4 = models.ManyToManyField(User, related_name='Opcion4')
    voto5 = models.ManyToManyField(User, related_name='Opcion5')

    def __str__(self):
        return "Encuesta de " + self.publicacion.titulo + " del usuario " + self.publicacion.autor.username
    