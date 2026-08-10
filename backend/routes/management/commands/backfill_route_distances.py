from django.contrib.gis.db.models.functions import Length
from django.core.management.base import BaseCommand

from routes.models import Route


class Command(BaseCommand):
    """Einmaliger Backfill für Route.distance_meters: Über Strava importierte Fahrten
    haben das Feld bisher nie befüllt bekommen und stehen deshalb auf dem Default 0 -
    sie zählen damit weder in die Kilometer der Lasche noch ins Profil oder das
    Gruppen-Leaderboard. Neue Importe setzen den Wert seitdem selbst (siehe
    core/views/strava.py), dieser Befehl trägt nur die Bestandsdaten nach.

    Die Länge kommt aus dem PostGIS-Feld geom (ST_LengthSpheroid, Ergebnis in Metern).
    Routen ohne geom - z.B. Strava-Aktivitäten ohne latlng-Stream - lassen sich so nicht
    nachberechnen und bleiben unverändert."""

    help = "Berechnet distance_meters für bestehende Routen aus deren geom nach."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Auch Routen neu berechnen, die bereits eine Distanz > 0 haben.',
        )

    def handle(self, *args, **options):
        routes = Route.objects.filter(geom__isnull=False)
        if not options['force']:
            routes = routes.filter(distance_meters=0)

        # .update() statt save() pro Instanz: das umgeht die post_save-Signale in
        # routes/signals.py, die sonst die Leistungs-Buckets ein zweites Mal aufaddieren
        # bzw. die Gruppen-Schnittmengen erneut berechnen würden.
        updated = routes.update(distance_meters=Length('geom'))
        self.stdout.write(self.style.SUCCESS(f"{updated} Route(n) aktualisiert."))

        missing = Route.objects.filter(geom__isnull=True, distance_meters=0).count()
        if missing:
            self.stdout.write(
                f"{missing} Route(n) ohne geom übersprungen - dort fehlen die Positionsdaten."
            )
