from django.db import models
from django.contrib.auth.models import User
from groups.models import Group

class PhotoPin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photo_pins')
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='photo_pins/')
    description = models.TextField(blank=True)
    groups = models.ManyToManyField(Group, related_name='photo_pins', blank=True)
    created_at = models.DateTimeField(auto_now_add=True);