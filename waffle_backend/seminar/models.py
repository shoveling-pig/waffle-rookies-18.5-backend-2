from django.db import models
from user.models import User

class Seminar(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(null=True)
    count = models.PositiveIntegerField(null=True)
    time = models.TimeField(max_length=500)
    online = models.CharField(max_length=500, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

# Mapping Table : User-Seminar
class UserSeminar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE)
    role = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(null=True)
    dropped_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)