from django.apps import AppConfig
import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder
from core.db_interface import DataBaseInterface

db_interface = None


class StrategyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'strategy_app'

    def ready(self):
        global db_interface
        print("Initializing strategy app...")
        db_interface = DataBaseInterface()
        print("Done !")
