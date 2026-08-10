from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField() #Damit das Frontend auf die eigene Profilseite verlinken kann (/user/:id)
    firstname = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()
    mail = serializers.SerializerMethodField()
    profilbild = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'firstname', 'lastname', 'mail', 'profilbild', 'onboarding_completed', 'latitude', 'longitude', 'location_name', 'group_invites_enabled', 'notifications_enabled']

    def get_id(self, obj):
        return obj.user.id


    # Name und E-Mail stehen ausschließlich am User. Die gleichnamigen Felder auf
    # UserProfile wurden mit Migration 0010 entfernt - die frühere Fallback-Kette
    # "obj.user.first_name or obj.firstname" warf deshalb bei jedem frisch
    # registrierten Konto einen AttributeError (first_name ist dort leer, also
    # wertete Python den rechten Operanden aus) und ließ /api/profil/ mit 500 enden.
    def get_firstname(self, obj):
        return obj.user.first_name

    def get_lastname(self, obj):
        return obj.user.last_name

    def get_mail(self, obj):
        return obj.user.email
    
    def get_profilbild(self, obj):
        if obj.profilbild:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profilbild.url)
            return obj.profilbild.url
        return None
    
    def update(self, instance, validate_data):
        user_data = validate_data.pop('user', None)

        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)

            new_email = user_data.get('email', user.email)
            if new_email:
                user.email = new_email
                user.username = new_email  # muss synchron zur E-Mail bleiben, sonst matched der Login (über username) nicht mehr

            user.save()
        return super().update(instance, validate_data)
