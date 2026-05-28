from rest_framework import serializers
from .models import Group

class GroupSerializer(serializers.ModelSerializers):

    is_admin = serializers.SerializerMethodField()
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'is_admin', 'member_count']#

        def get_is_admin(self, obj):
            user = self.context.get('request').user
            return obj.admin == user