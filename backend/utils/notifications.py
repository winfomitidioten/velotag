from firebase_admin import messaging
from users.models import UserDevice

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

        response = messaging.send_multicast(message)
        print(f"{response.success_count} Nachricht erfolgreich an {user.username} gesendet")
    except Exception as err:
        print(f"Push-Benachrichtigung an {user.username} fehlgeschlagen: {err}")
