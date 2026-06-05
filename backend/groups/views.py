from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.db.models import Q
from rest_framework.response import Response
from .serializers import GroupSerializer
from .models import Group
from rest_framework.authentication import TokenAuthentication
from users.models import User
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

class GroupDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)

            if group.admin != request.user and not group.members.filter(id=request.user.id).exists():
                return Response(
                    {"error": "Du hast keine Berechtigung, diese Gruppe anzuzeigen."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = GroupSerializer(group, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    def post(slef, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            if group.admin != request.user:
                return Response(
                    {"error": "Nur der Admin darf Mitglieder hinzufügen."}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            new_member_mail = request.data.get('email')
            if not new_member_mail:
                return Response(
                    {"error": "Eine Benutzermail wird benötigt."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_to_add = User.objects.get(email=new_member_mail)
            if group.members.filter(id=user_to_add.id).exists():
                return Response(
                    {"error": "Dieser Nutzer ist bereits Mitglied der Gruppe."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            group.members.add(user_to_add)
            serializer = GroupSerializer(group, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Es existiert kein Nutzer mit dieser E-Mail-Adresse."}, 
                status=status.HTTP_404_NOT_FOUND
            )  
    def delete(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            
            if group.admin != request.user:
                return Response(
                    {"error": "Nur der Admin darf Mitglieder entfernen."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            user_mail = request.data.get('email')
            if not user_mail:
                return Response(
                    {"error": "Eine Benutzermail wird benötigt."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            user_to_remove = User.objects.get(email=user_mail)
            group.members.remove(user_to_remove)
            serializer = GroupSerializer(group, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Es existiert kein Nutzer mit dieser E-Mail-Adresse."},
                status=status.HTTP_404_NOT_FOUND
            )
