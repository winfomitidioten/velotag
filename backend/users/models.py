from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profilbild = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Solo-Profil: wenn deaktiviert, darf niemand mehr diesen Nutzer in eine Gruppe einladen
    # (durchgesetzt serverseitig in GroupInviteAdmin, nicht nur clientseitig).
    group_invites_enabled = models.BooleanField(default=True)

    # Wenn deaktiviert, werden keine Push-Benachrichtigungen mehr verschickt
    # (durchgesetzt serverseitig in send_push_notifications, nicht nur clientseitig).
    notifications_enabled = models.BooleanField(default=True)
    onboarding_completed = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'Profil von {self.user.username}'

class StravaToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.IntegerField() # Unix-Timestamp

    def __str__(self):
        return f"Strava Token für {self.user.username}"

# Speichert die Push-Token der Geraete eines Nutzers (siehe utils/notifications.py).
# Ein Nutzer kann mehrere Geraete haben, push_token ist eindeutig pro Geraet/App-Installation.
class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    push_token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=50, default='android')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device von {self.user.username} ({self.platform})"