from rest_framework import serializers
from django.db.models import Prefetch
from user.models import User, ParticipantProfile, InstructorProfile
from seminar.models import Seminar, UserSeminar

class SeminarSerializer(serializers.ModelSerializer):

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
        userseminar = UserSeminar.objects.filter(seminar=seminar, role='participant')
        user = userseminar.user
        profile = user.participant
        return ParticipantProfileSerializer(profile, many=True).data

    def get_instructors(self, seminar):
        userseminar = UserSeminar.objects.filter(seminar=seminar, role='instructor')
        user = userseminar.user
        profile = user.instructor
        return InstructorProfileSerializer(profile, many=True).data

    def create(self, validated_data):
        seminar = Seminar.objects.create(**validated_data)
        return seminar

    def update(self, instance, validated):
        seminar = Seminar.objects.update(validated)
        return seminar

class ParticipantSerializer(serializers.ModelSerializer):
    university = serializers.CharField()
    accepted = serializers.BooleanField()
    seminars= serializers.SerializerMethodField()

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'university',
            'accepted',
            'seminars',
        )

    def get_seminars(self, profile):
        seminars = profile.user.userSeminar.all()
        return SeminarsSerializer(seminars, many=True).data


class InstructorSerializer(serializers.ModelSerializer):
    company = serializers.CharField()
    year = serializers.IntegerField()
    charge = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = (
            'id',
            'company',
            'year',
            'charge',
        )

    def get_charge(self, profile):
        charge = profile.user.userSeminar.all()
        return ChargeSerializer(charge).data

class SeminarsSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    joined_at = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    dropped_at = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'joined_at',
            'is_active',
            'dropped_at',
        )

    def get_joined_at(self, seminar):
        return seminar.userSeminar.joined_at

    def get_is_active(self, seminar):
        return seminar.userSeminar.is_active
    def get_dropped_at(self, seminar):
        return seminar.userSeminar.dropped_at

class ChargeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    joined_at = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'joined_at',
        )

    def get_joined_at(self, seminar):
        return seminar.userSeminar.joined_at

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