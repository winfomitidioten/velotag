import requests

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

NOMINATIM_USER_AGENT = 'velotag-app/1.0 (contact: support@velotag.de)'

from .serializers import UserProfileSerializer
from .models import UserProfile, UserDevice

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
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        location_name = request.data.get('location_name')

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

        has_coords = latitude not in (None, '') and longitude not in (None, '')
        if has_coords:
            try:
                lat_value = float(latitude)
                lon_value = float(longitude)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Ungültige Standort-Koordinaten.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            profile.latitude = lat_value
            profile.longitude = lon_value
        if location_name:
            profile.location_name = location_name

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
                password=password
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

class OnboardingView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        profilbild = request.data.get('profilbild')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        location_name = request.data.get('location_name')

        if not first_name or not last_name:
            return Response(
                {'error': 'Vorname und Nachname sind Pflichtfelder.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        has_coords = latitude not in (None, '') and longitude not in (None, '')
        if not has_coords and not location_name:
            return Response(
                {'error': 'Bitte gib deinen Standort an (Sensor oder manuelle Eingabe).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lat_value = None
        lon_value = None
        if has_coords:
            try:
                lat_value = float(latitude)
                lon_value = float(longitude)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Ungültige Standort-Koordinaten.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile.firstname = first_name
        profile.lastname = last_name
        if profilbild and not isinstance(profilbild, str):
            profile.profilbild = profilbild
        if has_coords:
            profile.latitude = lat_value
            profile.longitude = lon_value
        if location_name:
            profile.location_name = location_name
        profile.onboarding_completed = True
        profile.save()

        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class GeocodeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query')
        if not query:
            return Response(
                {'error': 'Bitte gib einen Suchbegriff an.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': query, 'format': 'json', 'limit': 1},
                headers={'User-Agent': NOMINATIM_USER_AGENT},
                timeout=5
            )
            response.raise_for_status()
            results = response.json()
        except (requests.RequestException, ValueError):
            return Response(
                {'error': 'Geocoding-Dienst ist aktuell nicht erreichbar.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if not results:
            return Response({'error': 'Ort nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)

        result = results[0]
        return Response({
            'latitude': float(result['lat']),
            'longitude': float(result['lon']),
            'display_name': result.get('display_name', query)
        }, status=status.HTTP_200_OK)

class GeocodeReverseView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')

        display_name = ''
        if lat and lon:
            try:
                response = requests.get(
                    'https://nominatim.openstreetmap.org/reverse',
                    params={'lat': lat, 'lon': lon, 'format': 'json'},
                    headers={'User-Agent': NOMINATIM_USER_AGENT},
                    timeout=5
                )
                response.raise_for_status()
                display_name = response.json().get('display_name', '')
            except (requests.RequestException, ValueError):
                # Reverse-Geocoding ist rein kosmetisch (Anzeige "deine Region") -
                # ein Fehler hier darf den Onboarding-Flow nicht blockieren
                display_name = ''

        return Response({'display_name': display_name}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete();
        return Response(status=204);

# Speichert den FCM-Push-Token eines Geraets fuer den eingeloggten Nutzer (siehe
# App.vue: setupAndroidPush() ruft diesen Endpoint nach PushNotifications.register() auf).
class DeviceView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform', 'android')

        if not token:
            return Response({'error': 'Token fehlt'}, status=400)

        device, created = UserDevice.objects.update_or_create(
            push_token=token,
            defaults={'user': request.user, 'platform': platform}
        )

        return Response({'status': 'success', 'created': created})

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
