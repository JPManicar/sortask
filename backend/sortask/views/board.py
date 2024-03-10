from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import Board
from ..serializers import BoardSerializer


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        project_id = self.kwargs['project_pk']
        serializer.save(project_id=project_id)

    def get_queryset(self):
        project_id = self.kwargs['project_pk']
        return Board.objects.filter(project_id=project_id)
