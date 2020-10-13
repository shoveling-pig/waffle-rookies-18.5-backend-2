from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token

from user.models import ParticipantProfile, InstructorProfile
from seminar.models import UserSeminar, Seminar

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    participant = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    role = serializers.ChoiceField(write_only=True, choices=UserSeminar.ROLES)
    university = serializers.CharField(write_only=True, allow_blank=True, required=False)
    accepted = serializers.BooleanField(write_only=True, default=True, required=False)
    company = serializers.CharField(write_only=True, allow_blank=True, required=False)
    year = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'last_login',
            'date_joined',
            'participant',
            'instructor',
            'role',
            'university',
            'accepted',
            'company',
            'year',
        )

    def get_participant(self, user):
        if hasattr(user, 'participant'):
            return ParticipantProfileSerializer(user.participant, context=self.context).data
        return None

    def get_instructor(self, user):
        if hasattr(user, 'instructor'):
            return InstructorProfileSerializer(user.instructor, context=self.context).data
        return None

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if bool(first_name) ^ bool(last_name):
            api_exception = serializers.ValidationError("First name and last name should appear together.")
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            api_exception = serializers.ValidationError("First name or last name should not have number.")
            api_exception.status_code = status.HTTP_404_BAD_REQUEST
            raise api_exception

        role = data.get('role')
        if role == UserSeminar.PARTICIPANT:
            profile_serializer = ParticipantProfileSerializer(data=data, context=self.context)
        else:
            profile_serializer = InstructorProfileSerializer(data=data, context=self.context)
        profile_serializer.is_valid(raise_exception=True)
        return data

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.pop('role')
        university = validated_data.pop('university', '')
        accepted = validated_data.pop('accepted', None)
        company = validated_data.pop('company', '')
        year = validated_data.pop('year', None)

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        if role == UserSeminar.PARTICIPANT:
            ParticipantProfile.objects.create(user=user, university=university, accepted=accepted)
        else:
            InstructorProfile.objects.create(user=user, company=company, year=year)

        return user

    def update(self, user, validated_data):
        if hasattr(user, 'participant'):
            participant_profile = user.participant
            university = validated_data.get('university')
            if university is not None:
                participant_profile.university = university
                participant_profile.save()
        if hasattr(user, 'instructor'):
            instructor_profile = user.instructor
            company = validated_data.get('company')
            year = validated_data.get('year')
            if company is not None or year:
                if company is not None:
                    instructor_profile.company = company
                if year:
                    instructor_profile.year = year
                instructor_profile.save()
        super(UserSerializer, self).update(user, validated_data)


class ParticipantProfileSerializer(serializers.ModelSerializer):
    accepted = serializers.BooleanField(default=True, required=False)
    seminars = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'university',
            'accepted',
            'seminars',
            'user_id',
        )

    def get_seminars(self, profile):
        seminars = profile.user.user_seminars.filter(role=UserSeminar.PARTICIPANT)
        return SeminarsSerializer(seminars, many=True, context=self.context).data

class InstructorProfileSerializer(serializers.ModelSerializer):
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
        user = profile.user
        try:
            charge = Seminar.objects.get(user_seminars__user=user, user_seminars__role='instructor')
            return ChargeSerializer(charge).data
        except Seminar.DoesNotExist:
            return None


class SeminarsSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(source='created_at')
    id = serializers.IntegerField(source='seminar.id')
    name = serializers.CharField(source='seminar.name')

    class Meta:
        model = UserSeminar
        fields = (
            'joined_at',
            'id',
            'name'
            'is_active',
            'dropped_at',
        )

class ChargeSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(source='created_at')
    id = serializers.IntegerField(source='seminar.id')
    name = serializers.CharField(source='seminar.name')

    class Meta:
        model = UserSeminar
        fields = (
            'joined_at',
            'id',
            'name',
        )