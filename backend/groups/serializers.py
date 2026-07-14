from rest_framework import serializers
from .models import Group, Membership
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
    admin_email = serializers.EmailField(source='admin.email', read_only=True)

    member_count = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    is_favorite = serializers.SerializerMethodField() #für Favoriten Stern in Gruppenansicht
    class Meta:
        model = Group
        fields = ['id', 'name', 'is_admin', 'member_count', 'members', 'admin_email', 'is_favorite']

    def get_is_admin(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.admin == request.user
        return False
    def get_members(self, obj):
        joined_users = User.objects.filter(
            membership__group=obj,
            membership__status='Joined'
        )
        return GrouMemberSerializer(joined_users, many=True, context=self.context).data
    def get_member_count(self, obj):
        return User.objects.filter(
            membership__group=obj,
            membership__status='Joined'
        ).count()
    
    #prüft, ob die Gruppe der Favorit des Users ist
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Membership.objects.filter(
                group=obj, 
                user=request.user, 
                is_favorite=True
            ).exists()
        return False