from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    lastname = serializers.CharField(source='user.last_name', required=False)
    firstname = serializers.CharField(source='user.first_name', required=False)
    mail = serializers.CharField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        fields = ['firstname', 'lastname', 'mail', 'profilbild']
    
    def update(self, instance, validate_data):
        user_data = validate_data.pop('user', {})
        user = instance.user

        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'email' in user_data:
            user.email = user_data['email']
        user.save()
        return super().update(instance, validate_data)