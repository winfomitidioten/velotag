from rest_framework import serializers
from .models import Group
from users.models import User

class GrouMemberSerializer(serializers.ModelSerializer):
    profilbild = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profilbild']

    def get_profilbild(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profilbild:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profilbild.url)
            return obj.profile.profilbild.url
        return None
class GroupSerializer(serializers.ModelSerializer):

    is_admin = serializers.SerializerMethodField()
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    members = GrouMemberSerializer(many=True, read_only=True)


    class Meta:
        model = Group
        fields = ['id', 'name', 'is_admin', 'member_count', 'members']

    def get_is_admin(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.admin == request.user
        return False