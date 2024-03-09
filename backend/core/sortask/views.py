from rest_framework.viewsets import ModelViewSet
from .models import Project, Board, Task, Checklist,  Comment, Member
from .serializers import (ProjectSerializer, BoardSerializer, TaskSerializer,
                          ChecklistSerializer, CommentSerializer, MemberSerializer)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class ChecklistViewSet(ModelViewSet):
    queryset = Checklist.objects.all()
    serializer_class = ChecklistSerializer


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
