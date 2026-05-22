from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = model.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    firstname = models.CharField(max_length=150, blank=True)
    lastname = models.CharField(max_length=150, blank=True)
    mail = models.EmailField(blank=True)

    profilbild = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'Profil von {self.user.username}'
