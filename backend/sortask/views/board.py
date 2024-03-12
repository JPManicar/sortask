from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Board
from ..serializers import BoardSerializer
from ..permissions import check_permission


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            response = check_permission(
                self.request.user, self.kwargs['project_pk'])

            if response:
                return response

        else:
            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
            return Response(new_error, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, project_pk):
        response = check_permission(self.request.user, project_pk)

        if response:
            return response

    def retrieve(self, request, project_pk):
        response = check_permission(self.request.user, project_pk)

        if response:
            return response

    def destroy(self, request, *args, **kwargs):
        response = check_permission(
            self.request.user, self.kwargs['project_pk'])

        if response:
            return response

    def perform_create(self, serializer):
        project_id = self.kwargs['project_pk']
        serializer.save(project_id=project_id)

    def get_queryset(self):
        project_id = self.kwargs['project_pk']
        return Board.objects.filter(project_id=project_id)
