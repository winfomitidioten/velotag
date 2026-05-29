from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.db.models import Q
from rest_framework.response import Response
from .serializers import GroupSerializer
from .models import Group
from rest_framework.authentication import TokenAuthentication
# Create your views here.

class GroupView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = Group.objects.filter(Q(admin = user) | Q(members=user)).distinct()

        serializer = GroupSerializer(groups, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        group_name = request.data.get('name')

        if not group_name:
            return Response(
                {"error": "Ein Gruppenname wird benötigt."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        new_group = Group.objects.create(
            name = group_name,
            admin = request.user
        )

        new_group.members.add(request.user)
        serializer = GroupSerializer(new_group, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)



