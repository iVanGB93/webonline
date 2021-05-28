from django.apps import AppConfig


class ServiciosConfig(AppConfig):
    name = 'servicios'

    def ready(self): 
        from .scheduler import tiempoAcabado       
        tiempoAcabado()   
        import servicios.signals
