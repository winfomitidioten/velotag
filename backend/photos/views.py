from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

from .serializers import PhotoPinCreateSerializer, PhotoPinListSerializer
from .models import PhotoPin
from groups.models import Group, Membership

class PhotoPinCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
        for image in images:            
            serializer = PhotoPinCreateSerializer(data={**base_data, 'image': image})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            created.append(serializer.data)

        return Response(created, status=status.HTTP_201_CREATED)
    
class PhotoPinListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        joined_groups = Group.objects.filter(membership__user=user, membership__status='Joined')
        pins = PhotoPin.objects.filter(
            Q(user=user) | Q(groups__in=joined_groups)
        ).distinct()

        serializer = PhotoPinListSerializer(pins, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PhotoPinGroupView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

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

