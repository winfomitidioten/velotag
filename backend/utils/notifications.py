import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from users.models import UserDevice

# Einmalige Initialisierung der Firebase Admin SDK beim ersten Import dieses Moduls.
# get_app() wirft ValueError, wenn noch keine Default-App existiert - das ist der
# offizielle Weg, mehrfaches initialize_app() (z.B. durch Djangos Autoreloader) zu
# vermeiden. Die Zugangsdaten liegen als lokale, nicht eingecheckte Datei pro
# Entwickler vor (aus der Firebase-Konsole exportiert).
try:
    firebase_admin.get_app()
except ValueError:
    cred_path = settings.BASE_DIR / 'firebase_credentials.json'
    if cred_path.exists():
        firebase_admin.initialize_app(credentials.Certificate(str(cred_path)))
    else:
        print("firebase_credentials.json nicht gefunden - Push-Benachrichtigungen sind deaktiviert.")

def send_push_notifications(user, title, body, data_payload=None):
    devices = UserDevice.objects.filter(user=user)

    if not devices.exists():
        print(f"Keine Geräte für den user gefunden")
        return

    tokens = [device.push_token for device in devices]
    if data_payload is None:
        data_payload = {}

    # Push-Versand ist ein reiner Nebeneffekt - ein Fehler hier (z.B. abgelaufener
    # Token, falsche Firebase-Credentials) darf die eigentliche Aktion des Aufrufers
    # (z.B. das Erstellen einer Gruppeneinladung) niemals mit einem 500er abbrechen.
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data_payload,
            tokens=tokens
        )

        # send_multicast() nutzt intern Googles /batch-Endpoint, den Google 2024
        # abgeschaltet hat (führt zu HTTP 404). send_each_for_multicast() ist der
        # offizielle Ersatz mit identischer Schnittstelle, ohne den Batch-Endpoint.
        response = messaging.send_each_for_multicast(message)
        print(f"{response.success_count} Nachricht erfolgreich an {user.username} gesendet")
    except Exception as err:
        print(f"Push-Benachrichtigung an {user.username} fehlgeschlagen: {err}")
