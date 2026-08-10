from rest_framework import serializers
from .models import PhotoPin

class PhotoPinCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoPin
        fields = ['latitude', 'longitude', 'image', 'description', 'groups']

class PhotoPinUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoPin
        fields = ['description', 'groups']  # 'image' intentionally excluded - the photo itself can't be replaced, only metadata

class PhotoPinListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    groups_ids = serializers.PrimaryKeyRelatedField(source='groups', many=True, read_only=True)  # raw group IDs, e.g. for pre-filling an edit form
    groups = serializers.SerializerMethodField()  # overrides the model field: [{id, name}, ...] for display instead of raw IDs
    is_owner = serializers.SerializerMethodField()
    uploader = serializers.SerializerMethodField()

    class Meta:
        model = PhotoPin
        fields = ['id', 'latitude', 'longitude', 'image', 'description', 'groups_ids', 'groups', 'created_at', 'is_owner', 'uploader']


    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and obj.user_id == request.user.id)  # user_id avoids an extra query for the related User row

    def get_uploader(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_groups(self, obj):
        return [{'id': group.id, 'name': group.name} for group in obj.groups.all()]