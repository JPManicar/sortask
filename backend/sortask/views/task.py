from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import Task
from ..serializers import TaskSerializer, TaskListSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return TaskListSerializer if self.action == 'list' else TaskSerializer

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)

        return instance

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project=project_id)

        assignee_ids = self.request.query_params.getlist('assignee_ids')
        if assignee_ids:
            # Convert string list to integer list for filtering
            assignee_ids = [int(id) for id in assignee_ids]
            queryset = queryset.filter(assignee__id__in=assignee_ids)

        return queryset
