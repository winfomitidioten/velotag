<<<<<<< HEAD
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserProfileSerializer
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework import status

# Create your views here.
class ProfileView(APIView):
    permissions_classes = [AllowAny]

    def get(self, request):
        user = User.objects.get(username="max.mustermann@stud.de")
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = User.objects.get(username="max.mustermann@stud.de")
        profile, created = UserProfile.objects.get_or_create(user=user)

        new_password = request.data.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
=======
from django.contrib.auth.models import update_last_login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        update_last_login(None, user)

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    
>>>>>>> origin/dev
