from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Project, Board, Task, CheckList, Comment, Member
from .serializers import (ProjectSerializer, ProjectListSerializer, BoardSerializer, TaskSerializer,
                          CheckListSerializer, CommentSerializer, MemberSerializer)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ProjectListSerializer if self.action == 'list' else ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(created_by=user)


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class ChecklistViewSet(ModelViewSet):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer
    permission_classes = [IsAuthenticated]


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
