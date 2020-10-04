from django.contrib import admin
from user.models import ParticipantProfile, InstructorProfile

# admin.site.register(User)
admin.site.register(ParticipantProfile)
admin.site.register(InstructorProfile)