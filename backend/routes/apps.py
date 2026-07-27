from django.apps import AppConfig


class RoutesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routes'

    # Diese Methode wird einmalig beim Start von Django aufgerufen
    def ready(self):
        # Wir importieren die signals.py hier drinnen, um zirkuläre Importe zu vermeiden!
        import routes.signals
