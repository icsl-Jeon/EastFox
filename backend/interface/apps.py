from django.apps import AppConfig
import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder


class StrategyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interface'

    def ready(self):
        pass
