from rest_framework import status
from rest_framework.response import Response
from .models import Member, Project


def check_permission(user, project_id):
    has_permission = Member.objects.filter(
        user=user, project_id=project_id).exists()
    if not has_permission:
        return Response({'error': 'You don\'t have permission to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    return None


def owns_project(user, project_id):
    print(f'user id: {user.id}\nproject_id: {project_id}\n{Project.objects.filter(id=project_id, created_by=user).exists()}')
    return Project.objects.filter(id=project_id, created_by=user).exists()
