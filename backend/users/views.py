from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserProfileSerializer
from django.contrib.auth.models import User

# Create your views here.
class ProfileView(APIView):
    permissions_classes = [AllowAny]

    def get(self, request):
        user = User.objects.get(username="max.mustermann@stud.de")
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    def patch(self, request):
        user = User.objects.get(username="max.mustermann@stud.de")

        new_password = request.data.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
        serializer = UserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)