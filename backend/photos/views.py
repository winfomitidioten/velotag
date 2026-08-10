from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from .serializers import PhotoPinCreateSerializer, PhotoPinListSerializer, PhotoPinUpdateSerializer
from .models import PhotoPin
from groups.models import Group, Membership

class PhotoPinCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(responses=PhotoPinCreateSerializer(many=True))
    def post(self, request):
        images = request.FILES.getlist('image')
        if not images:
            return Response({'image': 'Mindestens ein Foto ist erforderlich.'}, status=status.HTTP_400_BAD_REQUEST)
        
        base_data = {
            'latitude': request.data.get('latitude'),
            'longitude': request.data.get('longitude'),
            'description': request.data.get('description', ''),
            'groups': request.data.getlist('groups'),
        }

        created = []
        for image in images:  # jedes Bild wird ein eigener PhotoPin mit denselben Metadaten (base_data)
            serializer = PhotoPinCreateSerializer(data={**base_data, 'image': image})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # kein Rollback: bereits gespeicherte Bilder dieser Schleife bleiben bestehen
            serializer.save(user=request.user)
            created.append(serializer.data)

        return Response(created, status=status.HTTP_201_CREATED)
    
class PhotoPinListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=PhotoPinListSerializer(many=True))
    def get(self, request):
        # Die Solo-Ansicht zeigt ausschließlich die eigenen Pins - auch die, die einer
        # Gruppe zugeordnet sind. Fremde Pins aus gemeinsamen Gruppen erscheinen nur in
        # der Gruppenansicht (PhotoPinGroupView weiter unten).
        # Vorher stand hier zusätzlich Q(groups__in=joined_groups): dadurch tauchten
        # fremde Gruppenfotos auch in der Solo-Ansicht der anderen Mitglieder auf.
        pins = PhotoPin.objects.filter(user=request.user)

        serializer = PhotoPinListSerializer(pins, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PhotoPinGroupView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=PhotoPinListSerializer(many=True))
    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"error": "Gruppe wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
        if not Membership.objects.filter(user=request.user, group=group, status='Joined').exists():
            return Response({"error": "Du hast keine Berechtigung, diese Gruppe anzuzeigen."}, status=status.HTTP_403_FORBIDDEN)

        pins = PhotoPin.objects.filter(groups=group)
        serializer = PhotoPinListSerializer(pins, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PhotoPinDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_own_pin(self, request, pk):
        # setzt den Filter auf user=request.user, damit sind "fremde" Pins nicht erreichbar
        return PhotoPin.objects.filter(pk=pk, user=request.user).first()

    @extend_schema(responses=PhotoPinListSerializer)
    def patch(self, request, pk):
        pin = self.get_own_pin(request, pk)
        if pin is None:
            return Response({'error': 'Foto wurde nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PhotoPinUpdateSerializer(pin, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(PhotoPinListSerializer(pin, context={'request': request}).data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        pin = self.get_own_pin(request, pk)
        if pin is None:
            return Response({'error': 'Foto wurde nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
        pin.image.delete(save=False) # Bild wird aus /photo_pins/ gelöscht
        pin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        