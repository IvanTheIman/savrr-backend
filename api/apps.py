from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

class UsersCongif(AppConfig):
    name = 'users'

    def ready(self):
        import api.user_signals