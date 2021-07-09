from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Notificacion(models.Model):
    opcionesTipo = (
        ('RECARGA', 'RGA'),
        ('PAGO', 'PAG'),
        ('ENVIO', 'ENV'),
        ('RECIBO', 'REC'),
        ('MENSAJE', 'MSJ'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=opcionesTipo)
    contenido = models.CharField(max_length=250)
    vista = models.BooleanField(default=False) 

    def __str__(self):
        return self.usuario.username + " tipo: " + self.tipo + " Vista: " + str(self.vista)
    

def upload_to(instance, filename):
    return 'usuario/{filename}'.format(filename=filename)

class Profile(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)    
    imagen = models.ImageField(_("Image"), upload_to=upload_to, default='defaultUsuario.jpg')
    notificaciones = models.ManyToManyField(Notificacion)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username