from django.shortcuts import render
from django.core import signing
from rest_framework.views import APIView
from rest_framework import status, permissions, serializers
from django.db.models import Q, Sum, Count
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from .serializers import GroupSerializer, GrouMemberSerializer
from .models import Group, Membership
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from users.models import User, UserProfile
from utils.notifications import send_push_notifications
from routes.models import Route

# Create your views here.

class GroupView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # für den optionalen Bild-Upload
    serializer_class = GroupSerializer

    @extend_schema(responses=GroupSerializer(many=True))
    def get(self, request):
        user = request.user
        groups = Group.objects.filter(Q(membership__user=user, membership__status='Joined')).distinct()

        serializer = GroupSerializer(groups, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        group_name = request.data.get('name')

        if not group_name:
            return Response(
                {"error": "Ein Gruppenname wird benötigt."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profilbild = request.data.get('profilbild')
        new_group = Group.objects.create(
            name = group_name,
            description = request.data.get('description') or '',
            # profilbild kommt nur als echte Datei an, nie als String - so wird ein versehentlich
            # mitgeschicktes Textfeld (z.B. die bisherige Bild-URL) nie fälschlich übernommen.
            profilbild = profilbild if profilbild and not isinstance(profilbild, str) else None,
            admin = request.user
        )
        Membership.objects.create(user=request.user, group=new_group, status='Joined')
        serializer = GroupSerializer(new_group, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GroupDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # für den optionalen Bild-Upload
    serializer_class = GroupSerializer

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            if not Membership.objects.filter(user=request.user, group=group, status='Joined').exists():
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

    @extend_schema(responses=inline_serializer('GroupDeleteResponse', {'message': serializers.CharField()}))
    def delete(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            if not Membership.objects.filter(user=request.user, group=group, status='Joined').exists():
                return Response(
                    {"error": "Du hast keine Berechtigung, diese Gruppe anzuzeigen."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            if request.user != group.admin:
                return Response(
                    {"error": "Du hast keine Berechtigungen diese Gruppe zu löschen"},
                    status=status.HTTP_403_FORBIDDEN
                )
            group.delete()
            return Response(
                {"message": "Gruppe wurde erfolgreich gelöscht"},
                status=status.HTTP_200_OK
            )
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, pk):
        """
        Bearbeitet Name, Beschreibung und Profilbild einer Gruppe (nur Admin).
        Alle Felder sind optional und werden nur übernommen, wenn sie im Request
        vorkommen - so kann man z.B. nur das Bild ändern, ohne den Namen mitzuschicken.
        Löschen ohne Ersatz: description="" leert die Beschreibung, remove_profilbild="true"
        entfernt das Bild (beides ohne dass etwas Neues mitgeschickt werden muss).
        """
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != group.admin:
            return Response(
                {"error": "Nur der Admin darf die Gruppe bearbeiten."},
                status=status.HTTP_403_FORBIDDEN
            )

        name = request.data.get('name')
        if name is not None:
            if not name.strip():
                return Response(
                    {"error": "Ein Gruppenname wird benötigt."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            group.name = name

        description = request.data.get('description')
        if description is not None:
            group.description = description

        profilbild = request.data.get('profilbild')
        if profilbild and not isinstance(profilbild, str):
            group.profilbild = profilbild
        elif str(request.data.get('remove_profilbild', '')).lower() == 'true':
            group.profilbild = None

        group.save()
        serializer = GroupSerializer(group, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupLeaderboardView(APIView):
    """
    Bestenliste einer Gruppe nach gefahrenen Gesamt-km. Zaehlt bewusst ALLE
    Fahrten eines Mitglieds (Solo + andere Gruppen), nicht nur die in dieser
    Gruppe - das Ranking soll die Gesamtleistung der Person zeigen.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=inline_serializer('LeaderboardEntry', {
        'id': serializers.IntegerField(),
        'username': serializers.CharField(),
        'first_name': serializers.CharField(),
        'last_name': serializers.CharField(),
        'email': serializers.EmailField(),
        'profilbild': serializers.CharField(allow_null=True),
        'totalKm': serializers.IntegerField(),
        'rideCount': serializers.IntegerField(),
        'rank': serializers.IntegerField(),
    }, many=True))
    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not Membership.objects.filter(user=request.user, group=group, status='Joined').exists():
            return Response(
                {"error": "Du hast keine Berechtigung, diese Gruppe anzuzeigen."},
                status=status.HTTP_403_FORBIDDEN
            )

        members = User.objects.filter(membership__group=group, membership__status='Joined')

        # Ein Query statt N+1: Gesamtdistanz + Fahrtenanzahl pro Nutzer aggregiert,
        # ueber ALLE Routen der Mitglieder (kein Gruppenfilter auf Route).
        stats_by_user = {
            row['user']: row
            for row in Route.objects.filter(user__in=members).values('user').annotate(
                total_distance=Sum('distance_meters'),
                ride_count=Count('strecken_id')
            )
        }

        leaderboard = []
        for member in members:
            stats = stats_by_user.get(member.id)
            member_data = GrouMemberSerializer(member, context={'request': request}).data
            member_data['totalKm'] = round((stats['total_distance'] if stats else 0) / 1000)
            member_data['rideCount'] = stats['ride_count'] if stats else 0
            leaderboard.append(member_data)

        leaderboard.sort(key=lambda entry: entry['totalKm'], reverse=True)
        for index, entry in enumerate(leaderboard):
            entry['rank'] = index + 1

        return Response(leaderboard, status=status.HTTP_200_OK)


class GroupInviteAdmin(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializer

    def post(self, request, pk):
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
            membership = Membership.objects.filter(user=user_to_add, group=group).first()
            if membership:
                if membership.status == 'Pending':
                    return Response(
                        {"error": "Dieser Nutzer wurde bereits eingeladen, hat aber noch nicht angenommen"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if membership.status == 'Joined':
                    return Response(
                        {"error": "Dieser Nutzer ist bereits aktives Mitglied der Gruppe"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            target_profile, _ = UserProfile.objects.get_or_create(user=user_to_add)  # get_or_create, falls für den Nutzer noch kein Profil existiert
            if not target_profile.group_invites_enabled:
                return Response(
                    {"error": "Dieser Nutzer hat Gruppeneinladungen deaktiviert."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Membership.objects.create(user=user_to_add, group=group)  # status wird nicht gesetzt -> bleibt beim Model-Default 'Pending'
            serializer = GroupSerializer(group, context={'request': request})
            send_push_notifications(
                user=user_to_add,
                title="Neue Gruppeneinladung",
                body=f"{request.user.username} hat dich in eine Gruppe eingeladen",
                data_payload={
                    "type": "group_invitation"
                }
            )
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


# Salt + Gueltigkeitsdauer fuer die per Link/QR-Code verteilten Einladungs-Tokens
# (siehe GroupInviteLinkView / GroupJoinByTokenView unten).
GROUP_INVITE_LINK_SALT = 'group-invite-link'
GROUP_INVITE_LINK_MAX_AGE = 60 * 60 * 24 * 7  # 7 Tage gueltig


class GroupInviteLinkView(APIView):
    """
    Erzeugt einen signierten, zeitlich begrenzten Einladungs-Token fuer eine Gruppe.
    Damit koennen ein Einladungslink und ein QR-Code gebaut werden, ueber die neue
    Mitglieder beitreten koennen, ohne dass der Admin ihre E-Mail-Adresse kennen muss
    (Alternative zu GroupInviteAdmin, das die direkte E-Mail-Einladung abdeckt).
    Der Token selbst speichert nur die Gruppen-ID, es wird also keine Datenbank-
    aenderung fuer diese Funktion benoetigt.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=inline_serializer('GroupInviteLinkResponse', {'token': serializers.CharField()}))
    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if group.admin != request.user:
            return Response(
                {"error": "Nur der Admin darf einen Einladungslink erzeugen."},
                status=status.HTTP_403_FORBIDDEN
            )

        token = signing.dumps({'group_id': group.id}, salt=GROUP_INVITE_LINK_SALT)
        return Response({"token": token}, status=status.HTTP_200_OK)


class GroupJoinByTokenView(APIView):
    """
    Tritt einer Gruppe ueber einen von GroupInviteLinkView erzeugten Token bei
    (Klick auf den Einladungslink oder Scan des QR-Codes). Der eingeloggte Nutzer
    wird direkt als 'Joined'-Mitglied aufgenommen - er hat den Link/Code ja aktiv
    selbst genutzt, es ist also keine zusaetzliche Annahme wie bei der
    E-Mail-Einladung (Pending -> accept) noetig.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializer

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response(
                {"error": "Ein Einladungs-Token wird benötigt."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = signing.loads(token, salt=GROUP_INVITE_LINK_SALT, max_age=GROUP_INVITE_LINK_MAX_AGE)
        except signing.SignatureExpired:
            return Response(
                {"error": "Dieser Einladungslink ist abgelaufen."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except signing.BadSignature:
            return Response(
                {"error": "Dieser Einladungslink ist ungültig."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            group = Group.objects.get(pk=data['group_id'])
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        membership = Membership.objects.filter(user=request.user, group=group).first()
        if membership and membership.status == 'Joined':
            return Response(
                {"error": "Du bist bereits Mitglied dieser Gruppe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if membership:
            # War z.B. schon 'Pending' durch eine separate E-Mail-Einladung -
            # der Link bestaetigt den Beitritt dann direkt.
            membership.status = 'Joined'
            membership.save()
        else:
            Membership.objects.create(user=request.user, group=group, status='Joined')

        serializer = GroupSerializer(group, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserInvitationsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=GroupSerializer(many=True))
    def get(self, request):
            user = request.user
            groups = Group.objects.filter(Q(membership__user=user, membership__status='Pending')).distinct()
            serializer = GroupSerializer(groups, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=inline_serializer('InvitationActionResponse', {'message': serializers.CharField()}))
    def post(self, request):
        group_id = request.data.get('group_id')
        action = request.data.get('action')

        if not group_id or not action:
            return Response(
                {"error": "group_id und action werden benötigt"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if action not in ['accept', 'decline']:
            return Response(
                {"error": "Ungültige Aktion. Nur accept und decline erlaubt."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            membership = Membership.objects.get(user=request.user, group_id=group_id, status='Pending')

            if action == 'accept':
                membership.status = 'Joined'
                membership.save()
                return Response(
                    {"message": "Einladung erfolgreich angenommen"},
                    status=status.HTTP_200_OK
                )
            elif action == 'decline':
                membership.delete()
                return Response(
                    {"message": "Einladung erfolgreich abgelehnt"},
                    status=status.HTTP_200_OK
                )
        except Membership.DoesNotExist:
            return Response(
                {"error": "Keine offene Einladung für diese Gruppe gefunden"},
                status=status.HTTP_404_NOT_FOUND
            )
class GroupLeaveView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=inline_serializer('GroupLeaveResponse', {'message': serializers.CharField()}))
    def post(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(
                {"error": "Diese Gruppe existiert nicht"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        if not Membership.objects.filter(user=request.user, group=group, status='Joined').exists():
            return Response(
                {"error": "Dieser Nutzer ist kein aktives Mitglied der Gruppe"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if group.admin == request.user:
            # Admin verlässt die Gruppe: Rolle geht automatisch an ein anderes aktives Mitglied,
            # gibt es keins mehr wird die Gruppe komplett gelöscht statt admin-los zu bleiben.
            next_active_membership = Membership.objects.filter(
                group=group,
                status='Joined'
            ).exclude(user=request.user).first()

            if next_active_membership:
                group.admin = next_active_membership.user
                group.save()
            else:
                group.delete()
                return Response(
                    {"message": "Gruppe wurde gelöscht, da es keine anderen aktiven Mitglieder gibt"},
                    status=status.HTTP_200_OK
                )
                
        Membership.objects.filter(user=request.user, group=group).delete()
        return Response(
            {"message": "Du hast die Gruppe erfolgreich verlassen"},
            status=status.HTTP_200_OK
        )

class GroupKickView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializer

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
                
            user_to_remove = User.objects.get(email=user_mail)  # anders als bei GroupInviteAdmin/GroupTransferAdminView fehlt hier ein except User.DoesNotExist
            Membership.objects.filter(user=user_to_remove, group=group).delete()
            serializer = GroupSerializer(group, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Group.DoesNotExist:
            return Response(
                {"error": "Gruppe wurde nicht gefunden."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Membership.DoesNotExist:
            # unreachable: filter().delete() wirft nie DoesNotExist, das Entfernen eines Nicht-Mitglieds "gelingt" also einfach stillschweigend
            return Response(
                {"error": "Du bist kein aktives Mitglied dieser Gruppe."}, 
                status=status.HTTP_403_FORBIDDEN
            )

class GroupTransferAdminView(APIView):
    """
    Übergibt die Adminrolle einer Gruppe an ein anderes, bereits aktives Mitglied.
    `is_admin` im GroupSerializer wird direkt aus `group.admin == request.user` berechnet
    (siehe GroupSerializer.get_is_admin) - ein reiner Wechsel von `group.admin` reicht deshalb
    aus, um die Rechte beim neuen Admin zu aktivieren UND beim bisherigen Admin zu deaktivieren.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializer

    def post(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)

            if group.admin != request.user:
                return Response(
                    {"error": "Nur der Admin darf seine Rolle übertragen."},
                    status=status.HTTP_403_FORBIDDEN
                )

            new_admin_mail = request.data.get('email')
            if not new_admin_mail:
                return Response(
                    {"error": "Eine Benutzermail wird benötigt."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_admin = User.objects.get(email=new_admin_mail)
            if not Membership.objects.filter(user=new_admin, group=group, status='Joined').exists():
                return Response(
                    {"error": "Dieser Nutzer ist kein aktives Mitglied der Gruppe."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            group.admin = new_admin
            group.save()

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


class RemoveFavoriteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=inline_serializer('RemoveFavoriteResponse', {'message': serializers.CharField()}))
    def post(self, request):
        # Setzt einfach alle Favoriten des Users auf False
        Membership.objects.filter(user=request.user, is_favorite=True).update(is_favorite=False)
        return Response({"message": "Favorit erfolgreich entfernt."}, status=status.HTTP_200_OK)

class GetGroupFavoriteView(APIView):
    # Authentifizierung sicherstellen (wie bei deinen anderen Views)
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=inline_serializer('GroupFavoriteResponse', {'favorite_group_id': serializers.IntegerField(allow_null=True)}))
    def get(self, request):
        # 1. In der Membership-Tabelle nach der Zeile suchen, wo dieser User 
        # is_favorite=True gesetzt hat und (optional, aber gut) auch "Joined" ist.
        favorite_membership = Membership.objects.filter(
            user=request.user, 
            is_favorite=True,
            status='Joined'
        ).first()

        # 2. Wenn ein Favorit gefunden wurde, die group_id zurückgeben
        if favorite_membership:
            return Response(
                {"favorite_group_id": favorite_membership.group_id}, 
                status=status.HTTP_200_OK
            )
        
        # 3. Wenn kein Favorit existiert, senden wir null zurück
        return Response(
            {"favorite_group_id": None}, 
            status=status.HTTP_200_OK
        )
    
class SetGroupFavoriteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=inline_serializer('SetFavoriteResponse', {'message': serializers.CharField()}))
    def post(self, request, pk):
        try:
            # Prüfen, ob die Gruppe existiert
            group = Group.objects.get(pk=pk)
            
            # Prüfen, ob der User wirklich ein aktives Mitglied der Gruppe ist
            membership = Membership.objects.get(user=request.user, group=group, status='Joined')

            # 1. Bisherigen Favoriten des Users entfernen
            Membership.objects.filter(user=request.user, is_favorite=True).update(is_favorite=False)

            # 2. Neue Gruppe als Favorit speichern
            membership.is_favorite = True
            membership.save()

            return Response({"message": "Favorit erfolgreich aktualisiert."}, status=status.HTTP_200_OK)

        except Group.DoesNotExist:
            return Response(
                {"error": "Diese Gruppe existiert nicht."},
                status=status.HTTP_404_NOT_FOUND
            )