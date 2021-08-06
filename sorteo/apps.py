from django.apps import AppConfig


class SorteoConfig(AppConfig):
    name = 'sorteo'

    def ready(self): 
        import sorteo.signals