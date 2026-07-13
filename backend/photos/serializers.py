from rest_framework import serializers
from .models import PhotoPin

class PhotoPinCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoPin
        fields = ['latitude', 'longitude', 'image', 'description', 'groups']

class PhotoPinUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoPin
        fields = ['description', 'groups']

class PhotoPinListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    groups_ids = serializers.PrimaryKeyRelatedField(source='groups', many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = PhotoPin
        fields = ['id', 'latitude', 'longitude', 'image', 'description', 'groups_ids', 'created_at', 'is_owner']


    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and obj.user_id == request.user.id)