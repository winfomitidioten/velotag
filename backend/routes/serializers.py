from rest_framework import serializers
from .models import Route 

class RouteSerializer(serializers.ModelSerializer): # Aufgabe: RouteSerializer für die Eingabe der Strecken
    class Meta:
        model = Route
        # Exakt die Namen aus deinem Vue-Payload und der DB-Tabelle!
        fields = ['strecken_name', 'polyline_map', 'puls_stream', 'zeit_stream', 'watt_stream']
        
        read_only_fields = ['id', 'created_at', 'updated_at'] #Diese Felder werden automatisch von Django gesetzt, also nicht vom Frontend übergeben

        # Der User wird sicherheitshalber über das Login-Token gesetzt, nicht vom Frontend.
    