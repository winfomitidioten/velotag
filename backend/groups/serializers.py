from rest_framework import serializers
from .models import Group
from users.models import User

class GrouMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
class GroupSerializer(serializers.ModelSerializer):

    is_admin = serializers.SerializerMethodField()
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    members = GrouMemberSerializer(many=True, read_only=True)


    class Meta:
        model = Group
        fields = ['id', 'name', 'is_admin', 'member_count', 'members']

    def get_is_admin(self, obj):
        user = self.context.get('request').user
        return obj.admin == user