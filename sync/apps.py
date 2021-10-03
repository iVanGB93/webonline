from django.apps import AppConfig
from django.conf import settings

class SyncConfig(AppConfig):
    name = 'sync'

    if not settings.DEBUG:
        def ready(self): 
            from .scheduler import chequeo_conexiones       
            chequeo_conexiones()
