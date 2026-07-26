from rest_framework.views import APIView, csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RouteSerializer
from .serializers import RouteListSerializer
from .models import Route

from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Route

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
            # 3. Speichern und die user_id automatisch aus dem Request/Token ziehen
            serializer.save(user=request.user)
            
            return Response({"message": "Strecke erfolgreich gespeichert!"}, status=status.HTTP_201_CREATED)
            
        # 4. Falls das Frontend Quatsch schickt (z.B. falsche Datentypen), Fehler zurückgeben
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Für das Zeichnen der Fahrt
class RouteMapView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
    
# class RouteListView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self,request):
#         routes = Route.objects.filter(user=request.user)  # Nur Routen des eingeloggten Users
#         serializer = RouteListSerializer(routes, many=True)  # Liste → many=True
#         return Response(serializer.data, status=status.HTTP_200_OK)

# Einheitliche km-Statistik -> für Lasche, Profil, Bestenliste
class RouteStatsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(Route.get_stats_for_user(request.user), status=status.HTTP_200_OK)