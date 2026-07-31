from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField() #Damit das Frontend auf die eigene Profilseite verlinken kann (/user/:id)
    firstname = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    lastname = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    mail = serializers.EmailField(source='user.email', required=False)

    profilbild = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'firstname', 'lastname', 'mail', 'profilbild']

    def get_id(self, obj):
        return obj.user.id


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
                user.username = new_email

            user.save()
        return super().update(instance, validate_data)
