from django.apps import AppConfig


class PlaystyleCompassConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "playstyle_compass"

    def ready(self):
        import playstyle_compass.signals
