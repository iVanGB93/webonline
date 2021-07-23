from django.db import models

class EstadoConexion(models.Model):
    servidor = models.CharField(max_length=25)
    online = models.BooleanField(default=False)
    ip_online = models.GenericIPAddressField(blank=True, null=True)
    internet = models.BooleanField(default=False)
    ip_internet = models.GenericIPAddressField(blank=True, null=True)
    fecha_internet = models.DateTimeField(blank=True, null=True)
    jc = models.BooleanField(default=False)
    ip_jc = models.GenericIPAddressField(blank=True, null=True)
    emby = models.BooleanField(default=False)
    ip_emby = models.GenericIPAddressField(blank=True, null=True)
    ftp = models.BooleanField(default=False)
    ip_ftp = models.GenericIPAddressField(blank=True, null=True)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return "Conexiones de " + self.servidor
