from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.utils.crypto import get_random_string

def generarHash():    
    while True:
        code = get_random_string(length=8)
        if Oper.objects.filter(code=code).count() == 0:
            break
    return code

class Oper(models.Model):
    opcionesTipo = (
        ('RECARGA', 'RGA'),
        ('PAGO', 'PAG'),
        ('ENVIO', 'ENV'),
        ('RECIBO', 'REC'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    cantidad = models.IntegerField()
    servicio = models.CharField(max_length=15, null=True, blank=True)
    codRec = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=10, default=generarHash, unique=True)
    tipo = models.CharField(max_length=10, choices=opcionesTipo)
    haciaDesde = models.CharField(max_length=150, null=True, blank=True)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return self.tipo + self.usuario.username + str(self.cantidad)
    

def codigoRecarga():    
    while True:
        code = get_random_string(length=8, allowed_chars="1234567890")
        if Recarga.objects.filter(code=code).count() == 0:
            break
    return code


class Recarga(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=10, default=codigoRecarga, unique=True)
    cantidad = models.IntegerField()
    fechaHecha = models.DateTimeField(default=timezone.now)
    activa = models.BooleanField(default=True)
    fechaUso = models.DateTimeField(blank=True, null=True)
    creator = models.CharField(max_length=20, default="0n3")
    sync = models.BooleanField(default=False)

    def __str__(self):
        return self.code + " de " + str(self.cantidad) + " coins"
    

class EstadoServicio(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    internet = models.BooleanField(default=False)
    int_time = models.DateTimeField(null=True, blank=True)
    int_horas = models.IntegerField(null=True, blank=True)
    int_tipo = models.CharField(max_length=50, null=True, blank=True)
    int_duracion = models.CharField(max_length=50, null=True, blank=True)
    int_velocidad = models.CharField(max_length=50, null=True, blank=True)
    int_auto = models.BooleanField(default=False)
    emby = models.BooleanField(default=False)
    emby_time = models.DateTimeField(null=True, blank=True)
    emby_id = models.CharField(max_length=50, null=True, blank=True)
    emby_auto = models.BooleanField(default=False)
    jc = models.BooleanField(default=False)
    jc_time = models.DateTimeField(null=True, blank=True)
    jc_auto = models.BooleanField(default=False)
    ftp = models.BooleanField(default=False)
    ftp_time = models.DateTimeField(null=True, blank=True)
    ftp_auto = models.BooleanField(default=False)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return (f'Servicios de: {self.usuario.username}')
