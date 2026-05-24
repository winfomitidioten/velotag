import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save, sender=User)
def generate_random_username(sender, instance, **kwargs):
    if not instance.username:
        random_string = uuid.uuid4().hex
        instance.username = f"user_{random_string[:25]}"