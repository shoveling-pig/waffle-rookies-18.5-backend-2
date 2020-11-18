from rest_framework import serializers
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
        profile = seminar.user_seminars.filter(role=UserSeminar.PARTICIPANT)
        return ParticipantSerializer(profile, many=True, context=self.context).data

    def get_instructors(self, seminar):
        profile = seminar.user_seminars.filter(role=UserSeminar.INSTRUCTOR)
        return InstructorSerializer(profile, many=True, context=self.context).data

    def create(self, validated_data):
        seminar = Seminar.objects.create(**validated_data)
        return seminar

    def update(self, instance, validated):
        seminar = Seminar.objects.update(validated)
        return seminar

class ParticipantSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(source='created_at')
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = UserSeminar
        fields = (
            'joined_at',
            'is_active',
            'dropped_at',
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )

class InstructorSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(source='created_at')
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = UserSeminar
        fields = (
            'joined_at',
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )

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