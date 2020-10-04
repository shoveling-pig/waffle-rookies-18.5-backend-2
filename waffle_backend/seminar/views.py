import datetime
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from user.models import User, ParticipantProfile, InstructorProfile
from user.permissions import IsInstructor, IsParticipant
from seminar.models import Seminar, UserSeminar
from seminar.serializers import SeminarSerializer, MiniSeminarSerializer

class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.prefetch_related(
        Prefetch('user_seminars', queryset=UserSeminar.objects.select_related('seminar'), to_attr='seminar_userSeminar')
    )
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ('create', 'update'):
            return (IsInstructor(), )
        elif self.action == 'user' and self.request.method == 'DELETE':
            return (IsParticipant(), )
        return self.permission_classes

    def get_serializer_class(self):
        if self.action == 'list':
            return MiniSeminarSerializer
        return self.serializer_class

    # GET /api/v1/seminar/
    # GET /api/v1/seminar/?name={name}
    # GET /api/v1/seminar/?order=earliest
    def list(self, request):
        seminars = self.get_queryset()
        name = request.query_params.get('name')
        order = request.query_params.get('order')

        if name is not None:
            seminars = seminars.filter(name__contains=name)
        if order is not None:
            if order == 'earliest':
                seminars = seminars.order_by('-created_at')

        return Response(MiniSeminarSerializer(seminars, many=True).data, status=status.HTTP_200_OK)

    # GET /api/v1/seminar/{seminar_id}/
    def retrieve(self, request, pk=None):
        try:
            seminar = Seminar.objects.get(pk=pk)
        except Seminar.DoesNotExist:
            return Response({"error": "The seminar does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SeminarSerializer(seminar)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT /api/v1/seminar/{seminar_id}/
    def update(self, request, pk=None):
        user = request.user
        seminar = self.get_object()

        if not user.user_seminars.filter(seminar=seminar, role='instructor').exists():
            return Response({"error": "You're not the instructor of this seminar"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        serializer = self.get_serializer(seminar, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        participant_count = seminar.user_seminars.filter(role=UserSeminar.PARTICIPANT, is_active=True).count()
        if data.get('capacity') and int(data.get('capacity')) < participant_count:
            return Response({"error": "Capacity should be bigger than the number of participants"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.update(seminar, serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST /api/v1/seminar/{seminar_id}/user/
    # DELETE /api/v1/seminar/{seminar_id}/user/
    @action(detail=True, methods=['POST', 'DELETE'], url_path='user')
    def user(self, request, pk=None):
        if self.request.method == 'POST':
            user = request.user
            role = request.data.get['role']
            profile = ParticipantProfile.objects.filter(user=user)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            try:
                seminar = Seminar.objects.get(pk=pk)
            except Seminar.DoesNotExist:
                return Response({"error": "The seminar does not exist"}, status=status.HTTP_404_NOT_FOUND)

            if role is 'instructor' or role is 'participant':
                try:
                    user.userSeminar.filter(role=role)
                except UserSeminar.DoesNotExist:
                    return Response({"error": "The role is not valid"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"error": "The role is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            if role is 'participant':
                if not profile.accepted:
                    return Response({"error": "Your are not accepted"}, status=status.HTTP_403_FORBIDDEN)
                if serializer.get_participant_count(seminar) >= seminar.capacity:
                    return Response({"error": "This seminar is already full"}, status=status.HTTP_400_BAD_REQUEST)
            if role is 'instructor':
                if UserSeminar.objects.filter(user=user, role=role).count >= 1:
                    return Response({"error": "You are already other seminar's instructor"}, status=status.HTTP_400_BAD_REQUEST)
            if seminar.userSeminar.fliter(user=user).count >= 1:
                return Response({"error": "You are already in this seminar"}, status=status.HTTP_400_BAD_REQUEST)
            if not seminar.userSeminar.fliter(user=user).is_active:
                return Response({"error": "You were already dropped it"}, status=status.HTTP_400_BAD_REQUEST)

            userseminar = UserSeminar.objects.create(user=user, seminar=seminar, role=role, joined_at=datetime.datetime.now(), is_active=True)
            userseminar.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            user = request.user
            userseminar = UserSeminar.objects.filter(user=user)
            role = userseminar.role

            try:
                seminar = Seminar.objects.get(pk=pk)
            except Seminar.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            if (role is 'instructor') and (userseminar.seminar is seminar):
                return Response(status=status.HTTP_403_FORBIDDEN)

            userseminar = UserSeminar.objects.get(user=user, seminar=seminar)
            userseminar.update(is_active=False, dropped_at=datetime.datetime.now())
            userseminar.save()

            return Response(SeminarSerializer(seminar).data, status=status.HTTP_200_OK)

    # POST /api/v1/seminar/
    def create(self, request):
        user = request.user

        if user.user_seminars.filter(role='instructor').exists():
            return Response({"error": "You are already the instructor of other seminar"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seminar = serializer.save()

        UserSeminar.objects.create(user=user, seminar=seminar, role=UserSeminar.INSTRUCTOR)

        return Response(serializer.data, status=status.HTTP_201_CREATED)




