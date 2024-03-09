from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Board, Task, CheckList, Comment, Member
from .serializers import (ProjectSerializer, ProjectListSerializer, BoardSerializer, TaskSerializer,
                          CheckListSerializer, CommentSerializer, MemberSerializer)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def add_member(self, request, project_id):
        project = Project.objects.filter(id=project_id).first()

        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated:
            return Response({'error': 'You must be logged in to add members'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if user is already a member of the project
        if project.members.filter(user=request.user).exists():
            return Response({'error': 'You are already a member of this project'}, status=status.HTTP_400_BAD_REQUEST)

        # Add member to a project
        Member.objects.create(project=project, member=request.user)

        return Response({'message': 'Member added successfully'}, status=status.HTTP_201_CREATED)

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
