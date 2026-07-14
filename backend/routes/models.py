from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.db import models

class Route (models.Model): 
    strecken_id = models.AutoField(primary_key=True)
    strecken_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    group_id = models.JSONField(blank=True, null=True, help_text="Optional: ID der Gruppe, der die Strecke zugeordnet ist")
    polyline_map = models.TextField(blank=False, null=False, default="", help_text="Google Komprimierungsalgorithmus für Koordinaten")
    puls_stream = models.JSONField(blank=True, null=True, help_text="Array: Pulswerte")
    zeit_stream = models.JSONField(blank=False, null=False, default=list, help_text="Array: Zeitstempel für Geschwindigkeitslogik")
    watt_stream = models.JSONField(blank=True, null=True, help_text="Array: Wattwerte")

    start_time = models.DateTimeField(db_index=True, null=True, blank=True)
    end_time = models.DateTimeField(db_index=True, null=True, blank=True)
    geom = gis_models.LineStringField(srid=4326, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.strecken_name   
    


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