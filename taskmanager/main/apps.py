from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        #from main.llm_model import model_predict # Код из merger.py выполнится при старте
        import main.llm_model
