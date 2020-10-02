from django.shortcuts import render
from rest_framework import status, viewsets
from seminar.models import Seminar, UserSeminar

class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.prefetch_related(
        Prefetch('userSeminar', queryset=UserSeminar.objects.select_related('seminar'), to_attr='seminar_userSeminar')
    )
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)

    # GET /api/v1/seminar/
    # GET /api/v1/seminar/?name={name}
    # GET /api/v1/seminar/?order=earliest
    def list(self, request):
        seminars = self.get_queryset()
        name = self.context.get('request').query_params.get('name')
        order = self.contet.get('request').query_params.get('order')
        return Response(SeminarSerializer(seminars, many=True).data)

    # GET /api/v1/seminar/{seminar_id}/
    def retrieve(self, request, pk=None):
        try:
            seminar = Seminar.objects.get(pk=pk)
        except Seminar.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SeminarSerializer(seminar)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT /api/v1/seminar/{seminar_id}/
    def update(self, request, pk=None):
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT /api/v1/seminar/{seminar_id}/user/
    # POST /api/v1/seminar/{seminar_id}/user/
    # DELETE /api/v1/seminar/{seminar_id}/user/
    @action(detail=True, methods=['POST', 'PUT', 'DELETE'], url_path='user')
    def user(self, request, pk=None):
        if self.request.method == 'POST':
            user = request.user
            seminar = Seminar.objects.get(pk=pk)
            userseminar = UserSeminar.objects.filter(seminar=seminar, user=user)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if request.data.get['capacity'] < serializer.get_participant_count(seminar):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if userseminar.role != 'instructor':
                return Response({"error": "You are not the instructor of this seminar"}, status=status.HTTP_403_FORBIDDEN)

            return Response(serializer.data, status=status.HTTP_200_OK)

        elif self.request.method == 'POST':
            user = request.user
            role = request.data.get['role']
            try:
                seminar = Seminar.objects.get(pk=pk)
            except Seminar.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            userseminar = UserSeminar.objects.create(user=user, seminar=seminar, role=role, joined_at=datetime.datetime.now())
            userseminar.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            user = request.user
            role = request.data.get['role']

            try:
                seminar = Seminar.objects.get(pk=pk)
            except Seminar.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            if role == 'instructor':
                return Response(status=status.HTTP_403_FORBIDDEN)

            userseminar = UserSeminar.objects.get(user=user, seminar=seminar)
            userseminar.delete()
            userseminar.save()

            return Response(status=status.HTTP_200_OK)

    # POST /api/v1/seminar/
    def create(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not hasattr(user, 'instructor'):
            return Response({"error": "Only instructors can use this method."}, status=status.HTTP_403_FORBIDDEN)

        seminar = serializer.save()
        userseminar = UserSeminar.objects.create(user=user, seminar=seminar, joined_at=datetime.datetime.now())
        userseminar.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



