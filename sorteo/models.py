from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

class Sorteo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    servicio = models.CharField(max_length=15)
    eliminado = models.BooleanField(default=False)
    mes = models.CharField(max_length=10, default=timezone.now().month)
    fecha = models.DateTimeField(default=timezone.now)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username +  ", servicio: " + self.servicio + ", mes: " + self.mes + ", eliminado: " + str(self.eliminado)

class SorteoDetalle(models.Model):
    mes = models.CharField(max_length=10, default=timezone.now().month)
    activo = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)
    ganador = models.CharField(max_length=40, blank=True, null=True)
    recarga = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return "Sorteo del mes " + str(self.mes) + " ganador " + str(self.ganador) + " recarga " + str(self.recarga)
    