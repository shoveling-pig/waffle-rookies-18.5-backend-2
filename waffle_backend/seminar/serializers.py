from rest_framework import serializers
from seminar.models import Seminar, UserSeminar
from django.db.models import Prefetch

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

    def validate(self, data):
        name = data.get('name')
        capacity = data.get('capacity')
        count = data.get('count')
        time = data.get('time')
        online = data.get('online')
        if not (name and capacity and count and time):
            raise serializers.ValidationError("You should fill name, capacity, count and time")
        if capacity.isalpha() or count.isalpha():
            raise serializers.ValidationError("Capacity or count is not valid")
        if capacity<=0 or count<=0:
            raise serializers.ValidationError("Capacity and count should be positive integer")

        return data

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

    def get_participant_count(self, seminar):
        return seminar.userSeminar.filter(role='participant').count

    def create(self, validated_data):
        seminar = Seminar.objects.create(**validated_data)
        return seminar

    def update(self, instance, validated):
        seminar = Seminar.objects.update(validated)
        return seminar

# class MiniSeminarSerializer(serializers.ModelSerializer):
# class ChargeSerializer(serializers.ModelSerializer):

#class ParticipantSerializer(serializers.ModelSerializer):
# class InstructorSerializer(serializers.ModelSerializer):