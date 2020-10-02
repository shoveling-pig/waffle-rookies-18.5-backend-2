from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=500)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    last_login = models.TimeField(max_length=500)
    date_joined = models.TimeField(max_length=500)
    token = models.CharField(max_length=500, blank=True)
    # participant = models.ForeignKey(ParticipantProfile, null=True, related_name='user', on_delete=models.SET_NULL)
    # instructor = models.ForeignKey(ParticipantProfile, null=True, related_name='user', on_delete=models.SET_NULL)

class ParticipantProfile(models.Model):
    user = models.ForeignKey(User, related_name='participantprofiles', on_delete=models.CASCADE)
    university = models.CharField(max_length=500, blank=True)
    accepted = models.BooleanField(max_length=500, default=True, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

class InstructorProfile(models.Model):
    user = models.ForeignKey(User, related_name='instructorprofiles', on_delete=models.CASCADE)
    company = models.CharField(max_length=500, blank=True)
    year = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)
