from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=150, blank=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_groups')
    members = models.ManyToManyField(User, related_name='group_memberships')

    def __str__(self):
        return self.name