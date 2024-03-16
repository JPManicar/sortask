from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Project, Member
from ..serializers import ProjectSerializer, ProjectListSerializer
from ..permissions import owns_project


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ProjectListSerializer if self.action == 'list' else ProjectSerializer

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)

        # Add creator as member of a project
        Member.objects.create(project=instance, user=self.request.user)

        # Add default project boards
        instance.create_default_boards()

        return instance

    def update(self, request, *args, **kwargs):
        is_project_owner = owns_project(request.user, kwargs.get('pk'))

        if not is_project_owner:
            return Response({'error': "You don't have permission to update this project"}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, pk):
        is_project_owner = owns_project(request.user, self.kwargs.get('pk'))

        if not is_project_owner:
            return Response({'error': "You dont' have permission to delete this project"}, status=status.HTTP_403_FORBIDDEN)

        project = self.get_object()
        project.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = Project.objects.none()

        if self.action == 'list':
            user = self.request.user
            queryset = queryset.union(
                Project.objects.filter(members__user=user))

        else:
            pk = self.kwargs.get('pk')
            queryset = queryset.union(Project.objects.filter(id=pk))

        return queryset
