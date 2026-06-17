from rest_framework import serializers
from datetime import datetime, timezone
from .models import Route 

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        # Exakt die Namen aus deinem Vue-Payload und der DB-Tabelle!
        fields = ['strecken_name', 'polyline_map', 'puls_stream', 'zeit_stream', 'watt_stream']
        
        # Wichtig: user_id, created_at und updated_at lassen wir hier weg!
        # Der User wird sicherheitshalber über das Login-Token gesetzt, nicht vom Frontend.


class RouteListSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()
    avg_puls = serializers.SerializerMethodField()
    avg_watt = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ['strecken_id', 'strecken_name', 'created_at', 'duration_seconds', 'avg_puls', 'avg_watt']

    def get_duration_seconds(self, obj):
        stream = obj.zeit_stream
        if not stream or len(stream) < 2:
            return 0
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.strptime(stream[0], fmt).replace(tzinfo=timezone.utc)
        end = datetime.strptime(stream[-1], fmt).replace(tzinfo=timezone.utc)
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