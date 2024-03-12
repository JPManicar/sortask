from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from ..models import Project, Member
from ..serializers import ProjectSerializer, ProjectListSerializer


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

    def get_queryset(self):
        user = self.request.user

        # filter project if user is the creator or a member of
        projects = Project.objects.filter(
            Q(created_by=user) | Q(members__user=user))

        return projects
