from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Mensaje(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    visto = models.BooleanField(default=False)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return "Mensaje: " + self.contenido + ", de: " + self.autor.username

class Chat(models.Model):
    participantes = models.ManyToManyField(User)
    mensajes = models.ManyToManyField(Mensaje)
    grupo = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)
    sync = models.BooleanField(default=False)