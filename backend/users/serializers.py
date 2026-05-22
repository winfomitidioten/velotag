from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    lastname = serializers.CharField(source='last_name')
    firstname = serializers.CharField(source='first_name')
    mail = serializers.CharField(source='email')

    class Meta:
        model = UserProfile
        fields = ['firstname', 'lastname', 'mail', 'profilbild']