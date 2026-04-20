from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        # Import signals here if you have any
        try:
            import api.user_signals
        except ImportError:
            pass