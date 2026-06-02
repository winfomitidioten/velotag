from rest_framework import serializers
from .models import Route 

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        # Exakt die Namen aus deinem Vue-Payload und der DB-Tabelle!
        fields = ['strecken_name', 'polyline_map', 'puls_stream', 'zeit_stream', 'watt_stream']
        
        # Wichtig: user_id, created_at und updated_at lassen wir hier weg!
        # Der User wird sicherheitshalber über das Login-Token gesetzt, nicht vom Frontend.