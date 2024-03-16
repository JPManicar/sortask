from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Project, ProjectInvitation, Member
from ..permissions import owns_project


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
        is_project_owner = owns_project(request.user, project_id)

        if not is_project_owner:
            return Response({'error': "You dont' have permission to get invite link"}, status=status.HTTP_403_FORBIDDEN)

        project = Project.objects.filter(id=project_id).first()
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        invitation = ProjectInvitation.objects.filter(
            project_id=project_id).first()

        base_url = request.build_absolute_uri('/')

        if not invitation:
            invitation = ProjectInvitation.objects.create(
                project_id=project_id)

        return Response({'invitation_link': f'{base_url}v1/accept-invite/{invitation.token}'})
