from django.apps import AppConfig


class SuperuserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "superuser"

    def ready(self):
        import superuser.signals
