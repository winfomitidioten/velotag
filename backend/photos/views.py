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
        serializer = PhotoPinCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTPS_400_BAD_REQUEST)
    
class PhotoPinListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        joined_groups = Group.objects.filter(membership_user=user, membership_status='Joined')
        pins = PhotoPin.objects.filter(
            Q(user=user) | Q(groups_in=joined_groups)
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

