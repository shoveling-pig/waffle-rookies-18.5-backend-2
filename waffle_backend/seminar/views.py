from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.permissions import IsParticipant, IsInstructor
from seminar.models import Seminar, UserSeminar
from seminar.serializers import SeminarSerializer, MiniSeminarSerializer


class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        if self.action in ('create', 'update'):
            return (IsInstructor(), )
        elif self.action == 'user' and self.request.method == 'DELETE':
            return (IsParticipant(), )
        return super(SeminarViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return MiniSeminarSerializer
        return self.serializer_class

    # GET /api/v1/seminar/?name={name}&?order=earliest
    def list(self, request):
        name = request.query_params.get('name')
        order = request.query_params.get('order')

        seminars = self.get_queryset()
        if name:
            seminars = seminars.filter(name__icontains=name)
        if order == 'earliest':
            seminars = seminars.order_by('-created_at')
        else:
            seminars = seminars.order_by('created_at')

        return Response(SeminarSerializer(seminars, many=True).data, status=status.HTTP_200_OK)

    # GET /api/v1/seminar/{seminar_id}/
    def retrieve(self, request, pk=None):
        try:
            seminar = Seminar.objects.get(pk=pk)
        except Seminar.DoesNotExist:
            return Response({"error": "The seminar does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(SeminarSerializer(seminar).data, status=status.HTTP_200_OK)

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
    @action(detail=True, methods=['POST', 'DELETE'])
    def user(self, request, pk=None):
        try:
            seminar = Seminar.objects.get(pk=pk)
        except Seminar.DoesNotExist:
            return Response({"error": "Seminar does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if self.request.method == 'POST':
            return self._join_seminar(seminar)
        elif self.request.method == 'DELETE':
            return self._drop_seminar(seminar)

    def _join_seminar(self, seminar):
        user = self.request.user
        role = self.request.data.get('role')

        if role not in UserSeminar.ROLES:
            return Response({"error": "role should be participant or instructor"}, status=status.HTTP_400_BAD_REQUEST)

        if user.user_seminars.filter(seminar=seminar).exists():
            return Response({"error": "You've joined this seminar"}, status=status.HTTP_400_BAD_REQUEST)

        if role == UserSeminar.PARTICIPANT:
            if not hasattr(user, 'participant'):
                return Response({"error": "You're not a participant"}, status=status.HTTP_403_FORBIDDEN)
            if not user.participant.accepted:
                return Response({"error": "You're not accepted"}, status=status.HTTP_403_FORBIDDEN)

            with transaction.atomic():
                part_count = seminar.user_seminars.select_for_update().filter(
                    role=UserSeminar.PARTICIPANT,
                    is_active=True
                ).count()
                if part_count >= seminar.capacity:
                    return Response({"error": "You've joined this seminar"}, status=status.HTTP_400_BAD_REQUEST)

            UserSeminar.objects.create(user=user, seminar=seminar, role=UserSeminar.PARTICIPANT)
        else:
            if not hasattr(user, 'instructor'):
                return Response({"error": "You're not a instructor"}, status=status.HTTP_403_FORBIDDEN)
            if user.user_seminars.filter(role=UserSeminar.INSTRUCTOR).exists():
                return Response({"error": "Your're in charge of another seminar"}, status=status.HTTP_400_BAD_REQUEST)

            UserSeminar.objects.create(user=user, seminar=seminar, role=UserSeminar.INSTRUCTOR)

    def _drop_seminar(self, seminar):
        user = self.request.user

        if not user.user_seminars.filter(seminar=seminar).exists():
            return Response({"error": "You've joined this seminar"}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(user, 'participant'):
            return Response({"error": "Only participant can drop seminar"}, status=status.HTTP_403_FORBIDDEN)

        user_seminar = UserSeminar.objects.get(user=user, seminar=seminar, role=UserSeminar.PARTICIPANT)
        user_seminar.delete()

    # POST /api/v1/seminar/
    def create(self, request):
        user = request.user

        if user.user_seminars.filter(role='instructor').exists():
            return Response({"error": "You are already the instructor of other seminar"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        name = data.get('name')
        capacity = data.get('capacity')
        count = data.get('count')
        time = data.get('time')
        online = data.get('online')
        if not (bool(name) ^ bool(capacity) ^ bool(count) ^ bool(time) ^ bool(online)):
            return Response({"error","name, capacity, count, time and online fields are necessary"}, status=status.HTTP_400_BAD_REQUEST)
        elif (capacity <= 0) or (count <= 0):
            return Response({"error", "capacity and count should be positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seminar = serializer.save()

        UserSeminar.objects.create(user=user, seminar=seminar, role=UserSeminar.INSTRUCTOR)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




