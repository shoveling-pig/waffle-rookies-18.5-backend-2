from django.db import models
from user.models import User

class Seminar(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(null=True)
    count = models.PositiveIntegerField(null=True)
    time = models.TimeField(max_length=500)
    online = models.BooleanField(max_length=500, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Mapping Table : User-Seminar
class UserSeminar(models.Model):
    PARTICIPANT = 'participant'
    INSTRUCTOR = 'instructor'

    ROLE_CHOICES = (
        (PARTICIPANT, PARTICIPANT),
        (PARTICIPANT, INSTRUCTOR),
    )

    ROLES = (PARTICIPANT, INSTRUCTOR)

    user = models.ForeignKey(User, related_name='user_seminars', on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, related_name='user_seminars', on_delete=models.CASCADE)
    role = models.CharField(max_length=500, choices=ROLE_CHOICES, db_index=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(null=True) # 불확실
    dropped_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ('user', 'seminar')
        )