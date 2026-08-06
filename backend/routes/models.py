from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.gis.db import models as gis_models
from django.db import models

class Route (models.Model): 
    strecken_id = models.AutoField(primary_key=True)
    strecken_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    group_id = models.JSONField(blank=True, null=True, help_text="Optional: ID der Gruppe, der die Strecke zugeordnet ist")
    polyline_map = models.TextField(blank=False, null=False, default="", help_text="Google Komprimierungsalgorithmus für Koordinaten")
    distance_meters = models.FloatField(default=0, help_text="Gesamtdistanz der Strecke in Metern, berechnet beim Upload")
    puls_stream = models.JSONField(blank=True, null=True, help_text="Array: Pulswerte")
    zeit_stream = models.JSONField(blank=False, null=False, default=list, help_text="Array: Zeitstempel für Geschwindigkeitslogik")
    watt_stream = models.JSONField(blank=True, null=True, help_text="Array: Wattwerte")

    start_time = models.DateTimeField(db_index=True, null=True, blank=True)
    end_time = models.DateTimeField(db_index=True, null=True, blank=True)
    geom = gis_models.LineStringField(srid=4326, null=True, blank=True)
    strava_activity_id = models.BigIntegerField(null=True, blank=True, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.strecken_name   

    @staticmethod
    def get_stats_for_user(user):
        qs = Route.objects.filter(user=user)
        total_distance = qs.aggregate(total=Sum('distance_meters'))['total'] or 0
        return {
            'rideCount': qs.count(),
            'totalKm': round(total_distance/1000)
        }
    


class GroupRideIntersection(models.Model):
    #Schnittmenge der Fahrten einer Gruppe an einem bestimmten Tag. 
    #Wird automatisch berechnet, wenn eine neue Fahrt hochgeladen wird.
    
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='intersections')
    
    # db_index=True macht die Datenbankabfrage beim Kartenladen pfeilschnell
    date = models.DateField(db_index=True)
    
    # Hier speichert PostGIS unsere berechnete Schnittmenge als "Schlauch-Fläche"
    # srid=4326 ist der weltweite GPS-Standard (WGS84)
    geom = gis_models.MultiLineStringField(srid=4326, null=True, blank=True)
    
    class Meta:
        # Sorgt dafür, dass pro Gruppe und Tag maximal EINE Schnittmenge existieren kann.
        # Wird an diesem Tag eine neue Fahrt hochgeladen, überschreiben wir einfach diese Zeile!
        unique_together = ('group', 'date')

    def __str__(self):
        return f"Schnittmenge {self.group.name} am {self.date}"


class RouteLike(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'route'], name='unique_user_route_like')
        ]


class UserPerformanceBucket(models.Model):
    """Eine Rasterzelle (siehe routes/performance.py, PERFORMANCE_GRID_SIZE_METERS) für die
    Leistungs-Ansicht (Puls/Tempo/Watt) eines Users. Wird beim Hochladen einer Route inkrementell
    aktualisiert (siehe routes/signals.py) - nur der Beitrag der neuen Route wird addiert, nicht
    die komplette Historie neu berechnet. Dadurch bleibt das Kartenladen schnell, egal wie viele
    Routen der User insgesamt hat."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_buckets')
    grid_x = models.IntegerField()
    grid_y = models.IntegerField()

    # Repräsentative Geometrie dieser Zelle (vom ersten Segment, das hier hineinfiel)
    geom = gis_models.LineStringField(srid=4326)

    puls_sum = models.FloatField(default=0.0)
    puls_count = models.IntegerField(default=0)
    tempo_sum = models.FloatField(default=0.0)
    tempo_count = models.IntegerField(default=0)
    watt_sum = models.FloatField(default=0.0)
    watt_count = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'grid_x', 'grid_y'], name='unique_user_performance_bucket')
        ]
