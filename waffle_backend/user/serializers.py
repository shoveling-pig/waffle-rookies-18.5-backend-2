from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from seminar.models import UserSeminar
from seminar.serializers import MiniSeminarSerializer,ChargeSerializer


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=False)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    token = serializers.CharField(allow_blank=False)
    participant = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'last_login',
            'date_joined',
            'token',
            'participant',
            'instructor',
        )

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if bool(first_name) ^ bool(last_name):
            raise serializers.ValidationError("First name and last name should appear together.")
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            raise serializers.ValidationError("First name or last name should not have number.")
        return data

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        return user

    def update(self, instance, validated):
        user = super(UserSerializer, self).update(validated)
        return user

    def get_participant(self, part):
        return ParticipantProfileSerializer(part).data

    def get_instructor(self, inst):
        return InstructorProfileSerializer(inst).data


class ParticipantSerializer(serializers.ModelSerializer):
    university = serializers.CharField(allow_blank=False)
    accepted = serializers.BooleanField(required=False, default=True)
    seminars = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'university',
            'accepted',
            'seminars',
        )

    def get_seminars(self, user):
        userseminar = UserSeminar.objects.filter(user=user, role='participant')
        seminar = userseminar.seminar
        return MiniSeminarSerializer(seminar, many=True).data

class InstructorSerializer(serializers.ModelSerializer):
    company = serializers.CharField(allow_blank=False)
    year = serializers.IntegerField(required=False, allow_null=True)
    charge = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'company',
            'year',
            'charge',
        )

    def get_seminars(self, user):
        userseminar = UserSeminar.objects.filter(user=user, role='instructor')
        charge = userseminar.seminar
        return ChargeSerializer(charge).data
