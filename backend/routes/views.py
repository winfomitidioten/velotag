from rest_framework.views import APIView, csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RouteSerializer
from .serializers import RouteListSerializer
from .models import Route

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.gis.geos import LineString

from django.http import HttpResponse
from django.core.serializers import serialize
from .models import Route, GroupRideIntersection 
from groups.models import Group, Membership


def decode_polyline_to_postgis(polyline_str):#Hilfsfunktion, die den Google Encoded Polyline String in eine Liste von (Longitude, Latitude) Tuplen umwandelt
    """
    Decodiert einen Google Encoded Polyline String direkt in eine Liste von 
    (Longitude, Latitude) Tuplrn für GeoDjango/PostGIS.
    """
    index, lat, lng = 0, 0, 0
    coordinates = []
    
    while index < len(polyline_str):
        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1f) << shift
            shift += 5
            if not byte >= 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1f) << shift
            shift += 5
            if not byte >= 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        # WICHTIG: PostGIS braucht zwingend (Longitude, Latitude)! Format drehen!!
        coordinates.append((lng / 1e5, lat / 1e5))
        
    return coordinates
@method_decorator(csrf_exempt, name='dispatch')

class RouteCreateView(APIView): #Zweck: Diese View empfängt die POST-Anfrage vom Frontend, 
    #validiert die Daten mit dem RouteSerializer und speichert die Strecke in der DB
   
    authentication_classes = [TokenAuthentication] # Wir zwingen die View, NUR den Token zu akzeptieren (ignoriert CSRF)

    # Nur eingeloggte User dürfen Strecken hochladen
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # 1. Das JSON-Paket aus Vue an den Serializer übergeben
        serializer = RouteSerializer(data=request.data)
        
        # 2. Prüfen, ob die Daten sauber sind
        if serializer.is_valid():
            # 1. Den komprimierten String aus den validierten Daten holen
            polyline_str = serializer.validated_data.get('polyline_map')
            
            line_geom = None
            if polyline_str:
                # 2. Unsere Helferfunktion aufrufen (dreht Koordinaten automatisch um!)
                coords = decode_polyline_to_postgis(polyline_str)
                
                # 3. Das echte PostGIS LineString-Objekt (SRID 4326) erstellen
                if len(coords) >= 2:  # Eine GPS-Linie braucht mindestens 2 Punkte
                    line_geom = LineString(coords, srid=4326)
            
            # 4. Beim Speichern übergeben wir jetzt NICHT NUR den user, sondern auch geom!
            serializer.save(user=request.user, geom=line_geom)
            # 3. Speichern und die user_id automatisch aus dem Request/Token ziehen
            
            return Response({"message": "Strecke erfolgreich gespeichert!"}, status=status.HTTP_201_CREATED)
            
        # 4. Falls das Frontend Quatsch schickt (z.B. falsche Datentypen), Fehler zurückgeben
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Für das Zeichnen der Fahrt
class RouteMapView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        group_id = request.GET.get('group_id')

        if group_id:
            try:
                group_id_int = int(group_id)
                
                routes = Route.objects.filter(group_id__contains=group_id_int)
                
            except ValueError:
                return Response({"error": "Ungültige Gruppen-ID"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            routes = Route.objects.filter(user=request.user)
            
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#Für die Fahrten Anzeige
class RouteListView(APIView): #Zweck: Diese View empfängt die GET-Anfrage vom Frontend,
    #holt alle Strecken des eingeloggten Users aus der DB, serialisiert sie und schickt sie zurück

    authentication_classes = [TokenAuthentication] # Wir zwingen die View, NUR den Token zu akzeptieren (ignoriert CSRF)
    permission_classes = [IsAuthenticated] # Nur eingeloggte User dürfen ihre Strecken sehen

    def get(self, request):
        # 1. Alle Strecken des aktuellen Users aus der DB holen
        routes = Route.objects.filter(user=request.user)
        
        # 2. Die Strecken mit dem Serializer in JSON umwandeln
        serializer = RouteListSerializer(routes, many=True)
        
        # 3. Die JSON-Daten zurück an das Frontend schicken
        return Response(serializer.data, status=status.HTTP_200_OK)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_intersections_geojson(request, group_id):
    # 1. Sicherheits-Check: Existiert die Gruppe und ist der User Mitglied?
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Gruppe nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
    # Prüfen, ob der User in der Gruppe ist 
    # (WICHTIG: Passe "members" an, falls dein Feld in Group/Membership anders heißt!)
    if not Membership.objects.filter(user=request.user, group=group, status='Joined').exists():
        return Response({'error': 'Keine Berechtigung für diese Gruppe.'}, status=status.HTTP_403_FORBIDDEN)

    # 2. Alle berechneten Schnittmengen für diese Gruppe abrufen
    # Wir schließen leere Geometrien (falls mal was schiefging) sicherheitshalber aus
    intersections = GroupRideIntersection.objects.filter(group=group, geom__isnull=False)
    
    # 3. Djangos nativer GeoJSON-Serializer
    # Das ist der absolute Gamechanger: Er macht aus der SQL-Tabelle direkt valides Kartenmaterial
    geojson_data = serialize(
        'geojson', 
        intersections, 
        geometry_field='geom', 
        fields=('id', 'date')  # Diese Felder landen unter "properties" im GeoJSON
    )
    
    # 4. Als saubere JSON-Antwort an das Vue-Frontend schicken
    return HttpResponse(geojson_data, content_type='application/json')