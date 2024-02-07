from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from PIL import Image


class Notificacion(models.Model):
    opcionesTipo = (
        ('RECARGA', 'RGA'),
        ('PAGO', 'PAG'),
        ('ENVIO', 'ENV'),
        ('RECIBO', 'REC'),
        ('MENSAJE', 'MSJ'),
        ('REGISTRO', 'NEW'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=opcionesTipo)
    contenido = models.CharField(max_length=250)
    vista = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username + " tipo: " + self.tipo + " Vista: " + str(self.vista)
    

def upload_to(instance, filename):
    return 'usuario/{filename}'.format(filename=filename)

class Profile(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)
    subnet = models.CharField(max_length=50, default='local_iVan')
    imagen = models.ImageField(_("Image"), upload_to=upload_to, default='usuario/defaultUsuario.jpg')
    notificaciones = models.ManyToManyField(Notificacion)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.imagen.path)

        if img.height > 300 or img.width > 300:
           output_size = (300, 300)
           img.thumbnail(output_size)
           img.save(self.imagen.path)