from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint, Q

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=150, blank=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_groups')
    members = models.ManyToManyField(User, related_name='group_memberships', through='Membership')

    def __str__(self):
        return self.name

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=150, blank=False, default='Pending')

    is_favorite = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'group'],
                name='unique_user_group_membership'
            ),
            UniqueConstraint(
                fields=['user'],
                condition=Q(is_favorite=True),#Q Objekt ist in Django für komplexe Abfragen; hier: quasi "WHERE is_favorite = True"
                name='unique_user_favorite_group'
            )
        ]
        
