from django.db import models

class EstadoConexion(models.Model):
    servidor = models.CharField(max_length=25)
    online = models.BooleanField(default=False)
    ip_cliente = models.CharField(max_length=30, help_text="format: ip:puerto")
    internet = models.BooleanField(default=False)
    jc = models.BooleanField(default=False)
    emby = models.BooleanField(default=False)
    ftp = models.BooleanField(default=False)
    fecha_chequeo = models.DateTimeField(blank=True, null=True)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return "Conexiones de " + self.servidor
