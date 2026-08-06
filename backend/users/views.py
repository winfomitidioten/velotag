from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, update_last_login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import UserProfileSerializer
from .models import UserProfile

from groups.models import Membership
from routes.models import Route
from routes.serializers import RouteListSerializer



User = get_user_model()

class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        firstname = request.data.get('user.first_name')
        lastname = request.data.get('user.last_name')
        mail = request.data.get('user.email')
        password = request.data.get('password')
        profilbild = request.data.get('profilbild')
        group_invites_enabled = request.data.get('group_invites_enabled')
        notifications_enabled = request.data.get('notifications_enabled')

        if firstname is not None:
            user.first_name = firstname
        if lastname is not None:
            user.last_name = lastname
        if mail is not None:
            user.email = mail
        if password:
            user.set_password(password)
        user.save()
        
        if firstname is not None:
            profile.firstname = firstname
        if lastname is not None:
            profile.lastname = lastname
        if mail is not None:
            profile.mail = mail

        if profilbild and not isinstance(profilbild, str):
            profile.profilbild = profilbild

        if group_invites_enabled is not None:
            if isinstance(group_invites_enabled, str):
                profile.group_invites_enabled = group_invites_enabled.lower() == 'true'
            else:
                profile.group_invites_enabled = bool(group_invites_enabled)

        if notifications_enabled is not None:
            if isinstance(notifications_enabled, str):
                profile.notifications_enabled = notifications_enabled.lower() == 'true'
            else:
                profile.notifications_enabled = bool(notifications_enabled)

        profile.save()

        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        with open('debug_login.log', 'a', encoding='utf-8') as f:
            f.write(f"content_type={request.content_type!r} data={dict(request.data)!r}\n")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        update_last_login(None, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Bitte füllen Sie alle Pflichtfelder (E-Mail und Passwort) aus.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Ein Konto mit dieser E-Mail-Adresse existiert bereits.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    'message': 'Registrierung erfolgreich!',
                    'token': token.key
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Ein interner Fehler ist aufgetreten: {str(e)}\n Bitte wenden Sie sich an den Support oder versuchen Sie es später noch einmal.'}
            )

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete();
        return Response(status=204);

#Für die Profilansicht anderer Leute 
class PublicUserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Nutzer wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if target_user != request.user:
            shared_group_exists = Membership.objects.filter(
                user=request.user, status='Joined',
                group_id__in=Membership.objects.filter(user=target_user, status='Joined').values('group_id')
            ).exists()
            if not shared_group_exists:
                return Response({"error": "Du hast keine Berechtigung, dieses Profil anzusehen."}, status=status.HTTP_403_FORBIDDEN)

        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile_data = UserProfileSerializer(profile, context={'request': request}).data

        last_three = Route.objects.filter(user=target_user).order_by('-created_at')[:3]

        return Response({
            "profile": profile_data,
            "stats": Route.get_stats_for_user(target_user),
            "recentRides": RouteListSerializer(last_three, many=True).data
        }, status=status.HTTP_200_OK)
