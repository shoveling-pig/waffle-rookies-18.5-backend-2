from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.models import ParticipantProfile
from user.serializers import UserSerializer
from seminar.models import UserSeminar


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(), )
        return self.permission_classes

    # POST /api/v1/user/
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"error": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get[role] == 'participant':
            university = request.data.get('university')
            accepted = request.data.get('accpeted')
            if university is None:
                university = ""
            if accepted is None :
                accepted = True
            profile = ParticipantProfile(user=user, university=university, accepted=accepted)
            profile.save()
        elif request.data.get[role] == 'instructor':
            company = request.data.get('company')
            year = request.data.get('year')
            if company is None:
                company = ""
            if (not year.isdigit()) or (year<0):
                return Response({"error": "Year should be zero or positive integer."}, status=status.HTTP_400_BAD_REQUEST)
            profile = InstructorProfile(user=user, company=company, year=year)
            profile.save()
        else:
            return Response({"error": "Your role is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        data = serializer.data
        data['token'] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /api/v1/user/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            data = self.get_serializer(user).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            return Response(data)

        return Response({"error": "Wrong username or wrong password"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        return Response()

    # Get /api/v1/user/{user_id}
    def retrieve(self, request, pk=None):
        user = request.user if pk == 'me' else self.get_object()
        return Response(self.get_serializer(user).data)

    # PUT /api/v1/user/me/
    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't update other Users information"}, status=status.HTTP_403_FORBIDDEN)

        user = request.user

        userseminar = UserSeminar.objects.filter(user=user)
        if userseminar.role == 'participant':
            if not request.data.get('university') or (request.data.get('university') is '\0'):
                request.data.get['university'] = ""
        elif userseminar.role == 'instructor':
            if not request.data.get['company'] or (request.data.get['company'] is '\0'):
                request.data.get['company'] = ""
            if (not request.data.get('year').isdigit()) or (request.data.get('year')<0):
                return Response({"error": "Year should be zero or positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)
        serializer.save()
        return Response(serializer.data)

    # POST /api/v1/user/participant/
    @action(detail=False, methods=['POST'], url_path='participant', url_name='participant')
    def participant(self, request):
        user = request.user

        if request.data.get['university'] is None:
            request.data.get['university'] = ""
        if request.data.get['accepted'] is None:
            request.data.get['accepted'] = True

        try:
            profile = ParticipantProfile(user=user, university=request.data.get[university])
            profile.save()
        except IntegrityError:
            return Response({"error": "A profile with that user already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)