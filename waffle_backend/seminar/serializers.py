from rest_framework import serializers
from django.db.models import Prefetch
from user.models import User, ParticipantProfile, InstructorProfile
from seminar.models import Seminar, UserSeminar
import datetime

class SeminarSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format='%H:%M')
    online = serializers.BooleanField(default=True)
    participants = serializers.SerializerMethodField()
    instructors = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'capacity',
            'count',
            'time',
            'online',
            'instructors',
            'participants',
        )

    def get_participants(self, seminar):
        profile = ParticipantProfile.objects.filter(user__userseminar__seminar=seminar, user__userseminar__role='participant')
        return ParticipantSerializer(profile, many=True).data

    def get_instructors(self, seminar):
        profile = InstructorProfile.objects.filter(user__userseminar__seminar=seminar, user__userseminar__role='instructor')
        return InstructorSerializer(profile, many=True).data

    def create(self, validated_data):
        seminar = Seminar.objects.create(**validated_data)
        return seminar

    def update(self, instance, validated):
        seminar = Seminar.objects.update(validated)
        return seminar

class ParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    joined_at = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    dropped_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_at',
            'is_active',
            'dropped_at',
        )

    def get_joined_at(self, user):
        return user.userSeminar.joined_at
    def get_is_active(self, user):
        return user.userSeminar.is_active
    def get_dropped_at(self, user):
        return user.userSeminar.dropped_at

class InstructorSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    joined_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_at',
        )

    def get_joined_at(self, user):
        return user.userSeminar.joined_at

class MiniSeminarSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    instructors = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'instructors',
            'participant_count',
        )

    def get_instructors(self, seminar):
        instructors = seminar.userSeminar.filter(role='instructor')
        return InstructorSerializer(instructors, many=True).data

    def get_participant_count(self, seminar):
        return seminar.userSeminar.filter(role='participant', is_active=True).count