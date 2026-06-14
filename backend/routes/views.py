from rest_framework.views import APIView, csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RouteSerializer
from .serializers import RouteListSerializer
# NEU: Diese Zeile fehlt, damit Python weiß, was TokenAuthentication ist!
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Route

@method_decorator(csrf_exempt, name='dispatch')

class RouteCreateView(APIView):
    # NEU: Wir zwingen die View, NUR den Token zu akzeptieren (ignoriert CSRF!)
    authentication_classes = [TokenAuthentication]

    # WINF-Sicherheitsregel: Nur eingeloggte User dürfen Strecken hochladen!
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
    
class RouteListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        routes = Route.objects.filter(user=request.user)  # Nur Routen des eingeloggten Users
        serializer = RouteListSerializer(routes, many=True)  # Liste → many=True
        return Response(serializer.data, status=status.HTTP_200_OK)