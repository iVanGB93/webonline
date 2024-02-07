from django.apps import AppConfig


class ServiciosConfig(AppConfig):
    name = 'servicios'

    def ready(self):
        import servicios.signals
