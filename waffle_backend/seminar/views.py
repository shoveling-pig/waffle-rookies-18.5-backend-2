from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
import datetime
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from user.models import User, ParticipantProfile
from seminar.models import Seminar, UserSeminar
from seminar.serializers import SeminarSerializer, MiniSeminarSerializer

class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.prefetch_related(
        Prefetch('userSeminar', queryset=UserSeminar.objects.select_related('seminar'), to_attr='seminar_userSeminar')
    )
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated(),)

    # GET /api/v1/seminar/
    # GET /api/v1/seminar/?name={name}
    # GET /api/v1/seminar/?order=earliest
    def list(self, request):
        seminars = self.get_queryset()

        name = self.context.get('request').query_params.get('name')
        order = self.contet.get('request').query_params.get('order')

        if name is not None:
            seminars = seminars.filter(name__contains==name)
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

        try:
            seminar = Seminar.objects.get(pk=pk)
        except Seminar.DoesNotExist:
            return Response({"error": "The seminar does not exist"}, status=status.HTTP_404_NOT_FOUND)

        userseminar = UserSeminar.objects.filter(seminar=seminar, user=user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.data.get['capacity'] < serializer.get_participant_count(seminar):
            return Response({"error": "capacity is smaller than participant count"}, status=status.HTTP_400_BAD_REQUEST)
        if userseminar.role is not 'instructor':
            return Response({"error": "You are not the instructor of this seminar"}, status=status.HTTP_403_FORBIDDEN)

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = request.data.get('name')
        capacity = request.data.get('capacity')
        count = request.data.get('count')
        time = request.data.get('time')
        online = request.data.get('online')

        if not hasattr(user, 'instructor'):
            return Response({"error": "Only instructors can use this method."}, status=status.HTTP_403_FORBIDDEN)
        if not (name and capacity and count and time):
            return Response({"error": "name, capacity, count and time must filled"}, status=status.HTTP_400_BAD_REQUEST)
        if not capacity.isdigit() or not count.isdigit():
            return Response({"error": "capacity and count should be a number"}, status=status.HTTP_400_BAD_REQUEST)
        if capacity<=0 or count<=0:
            return Response({"error": "capacity and count should be positive integer"}, status=status.HTTP_400_BAD_REQUEST)
        if name == '\0':
            return Response({"error": "name is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        if online is None:
            request.data.get['online'] = ""
        try:
            datetime.datetime.strptime(time, '%H:%M')
        except:
            Response({"error": "time is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        seminar = serializer.save()
        userseminar = UserSeminar.objects.create(user=user, seminar=seminar, joined_at=datetime.datetime.now())
        userseminar.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)




