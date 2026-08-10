import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save, sender=User)
def generate_random_username(sender, instance, **kwargs):
    # Fallback für Erstellungswege ohne username (z.B. Admin-Formular in users/admin.py,
    # das nur email/password abfragt) - das User-Model verlangt trotzdem ein unique username
    if not instance.username:
        random_string = uuid.uuid4().hex
        instance.username = f"user_{random_string[:25]}"