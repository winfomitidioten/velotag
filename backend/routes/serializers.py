from rest_framework import serializers
from datetime import datetime
from .models import Route 
from groups.models import Group
from django.contrib.gis.geos import LineString  # 1. NEU: Import für Djangos Geometrie-Objekt

class RouteSerializer(serializers.ModelSerializer):
    #nur für Zwischenschritt coordinates => geom Feld 
    coordinates = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField()),
        write_only=True,
        required=False
    )

    class Meta:
        model = Route
        fields = ['strecken_name', 
                  'group_id', 
                  'polyline_map', 
                  'puls_stream', 
                  'zeit_stream', 
                  'watt_stream', 
                  'start_time',
                  'end_time', 
                  'coordinates',
                  'geom']
        
        read_only_fields = ['geom']#geom wird im Backend aus coordinates berechnet

    # 2. NEU: Hier überschreiben wir den standardmäßigen Speichervorgang
    def create(self, validated_data):
        # A) Das Array aus den validierten Daten "aufpoppen" (entfernen & zwischenspeichern).
        # Wichtig: Wenn wir .pop() nicht nutzen würden, würde Django versuchen, 
        # ein Feld namens 'coordinates' in der DB zu speichern und abstürzen!
        coords = validated_data.pop('coordinates', None)
        
        # B) Prüfen, ob Koordinaten mitgeschickt wurden und eine Linie bilden (min. 2 Punkte)
        if coords and len(coords) >= 2:
            # Wir bauen aus der Array-Liste eine echte PostGIS-Linie im GPS-Format (SRID 4326)
            validated_data['geom'] = LineString(coords, srid=4326)
            
        # C) Die fertigen Daten an die Standard-Funktion weitergeben, 
        # die jetzt ein sauberes 'geom'-Objekt (aber kein 'coordinates'-Array mehr) enthält
        return super().create(validated_data)

class RouteListSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()
    avg_puls = serializers.SerializerMethodField()
    avg_watt = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ['strecken_id', 'strecken_name', 'created_at', 'duration_seconds', 'avg_puls', 'avg_watt', 'group_id', 'groups']

    
    def get_duration_seconds(self, obj):
        stream = obj.zeit_stream
        if not stream or len(stream) < 2 or stream[0] is None or stream[-1] is None:
            return 0

        # GPX-Zeitstempel kommen roh aus der Datei (siehe useGPXVerarbeitung.js) und variieren
        # je nach Gerät/App leicht im Format (mit/ohne Millisekunden). Ein zu starres strptime-Format
        # ließ die Serialisierung hier bei abweichenden Zeitstempeln mit ValueError abstürzen -
        # und riss damit die komplette Fahrten-Liste mit sich (500-Fehler, Frontend zeigt "keine Fahrten").
        try:
            start = datetime.fromisoformat(stream[0].replace('Z', '+00:00'))
            end = datetime.fromisoformat(stream[-1].replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError):
            return 0
        return int((end - start).total_seconds())

    def get_avg_puls(self, obj):
        stream = obj.puls_stream
        if not stream:
            return None
        values = [float(x) for x in stream if x is not None]
        return int(sum(values) / len(values)) if values else None

    def get_avg_watt(self, obj):
        stream = obj.watt_stream
        if not stream:
            return None
        values = [float(x) for x in stream if x is not None]
        return int(sum(values) / len(values)) if values else None
    
    def get_groups(self,obj):
        if not obj.group_id:
            return []
        return list(Group.objects.filter(id__in=obj.group_id).values('id', 'name')) # groups liefert id, name für die Badges in der Liste 


# # schlankerer Serializer ohne Polyline und mit berechneten Werten für die Strecken Liste
# class RouteListSerializer(serializers.ModelSerializer):
#     duration_seconds = serializers.SerializerMethodField()
#     avg_puls = serializers.SerializerMethodField()
#     avg_watt = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Route
#         fields = ['strecken_id', 'strecken_name', 'created_at', 'duration_seconds', 'avg_puls', 'avg_watt']
    
#     def get_duration_seconds(self, obj):
#         stream = obj.zeit_stream
#         if not stream or len(stream) < 2: 
#             return 0 
#         return int(stream[-1] - stream[0])
    
#     def get_avg_puls(self, obj):
#         stream = obj.puls_stream
#         if not stream: #Prüft ob der Stream leer ist, um Fehler bei /0 vorzubeugen
#             return None
#         return int(sum(stream) / len(stream))
    
#     def get_avg_watt(self, obj):
#         stream = obj.watt_stream
#         if not stream:
#             return None
#         return int(sum(stream) / len(stream))