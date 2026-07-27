from django.core.management.base import BaseCommand
from routes.models import Route, UserPerformanceBucket
from routes.performance import persist_route_contributions


class Command(BaseCommand):
    """Einmaliger Backfill für UserPerformanceBucket: berechnet die Puls-/Tempo-/Watt-Raster
    für alle bereits vor Einführung der Leistungs-Ansicht hochgeladenen Routen nach.
    Neue Routen werden automatisch über routes/signals.py inkrementell erfasst - dieser Befehl
    ist nur für den einmaligen Nachtrag der Bestandsdaten nötig."""
    help = "Berechnet UserPerformanceBucket-Zeilen für alle bestehenden Routen mit geom neu."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Löscht vorher alle bestehenden UserPerformanceBucket-Zeilen (verhindert Doppelzählung bei erneutem Lauf).',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = UserPerformanceBucket.objects.all().delete()
            self.stdout.write(f"{deleted} bestehende Bucket-Zeilen gelöscht.")

        routes = Route.objects.filter(geom__isnull=False)
        total = routes.count()
        self.stdout.write(f"Verarbeite {total} Routen mit Geometrie...")

        for i, route in enumerate(routes, start=1):
            persist_route_contributions(route)
            self.stdout.write(f"  [{i}/{total}] Route {route.strecken_id} ({route.strecken_name}) verarbeitet")

        self.stdout.write(self.style.SUCCESS("Backfill abgeschlossen."))
