from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint 

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

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'group'],
                name='unique_user_group_membership'
            )
        ]
