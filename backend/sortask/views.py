from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Project, ProjectInvitation, Board, Task, CheckList, Comment, Member
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


class ProjectInvitationViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def accept_invite(self, request, token):
        invitation = ProjectInvitation.objects.filter(token=token).first()

        if not invitation:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)

        project = Project.objects.filter(id=invitation.project_id).first()

        # Check if user is already a member of the project
        if project.members.filter(user=request.user).exists():
            return Response({'error': 'You are already a member of this project'}, status=status.HTTP_400_BAD_REQUEST)

        # Add member to a project
        Member.objects.create(project=project, user=request.user)

        return Response({'message': f'You\'ve successfully joined the project {project.title}'}, status=status.HTTP_201_CREATED)

    def get_invite_link(self, request, project_id):
        project = Project.objects.filter(id=project_id).first()
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        invitation = ProjectInvitation.objects.filter(
            project_id=project_id).first()

        base_url = request.build_absolute_uri('/')

        if not invitation:
            invitation = ProjectInvitation.objects.create(
                project_id=project_id)

        return Response({'invitation_link': f'{base_url}/v1/accept-invite/{invitation.token}'})


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
