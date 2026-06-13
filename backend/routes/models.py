from django.db import models
from django.contrib.auth.models import User

class Route (models.Model): 
    strecken_id = models.AutoField(primary_key=True)
    strecken_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    polyline_map = models.TextField(blank=False, null=False, default="", help_text="Google Komprimierungsalgorithmus für Koordinaten")
    puls_stream = models.JSONField(blank=True, null=True, help_text="Array: Pulswerte")
    zeit_stream = models.JSONField(blank=False, null=False, help_text="Array: Zeitstempel für Geschwindigkeitslogik")
    watt_stream = models.JSONField(blank=True, null=True, help_text="Array: Wattwerte")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.strecken_name   