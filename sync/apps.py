from django.apps import AppConfig


class SyncConfig(AppConfig):
    name = 'sync'

    def ready(self): 
        from .scheduler import chequeo_conexiones       
        chequeo_conexiones()
