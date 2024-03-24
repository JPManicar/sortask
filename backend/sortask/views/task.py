from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
import django_filters
from ..models import Task, Notification, Member
from ..serializers import TaskSerializer, TaskListSerializer, UserFullNameSerializer
from ..permissions import check_permission


class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Task
        fields = ['title']


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TaskFilter

    def get_serializer_class(self):
        return TaskListSerializer if self.action == 'list' else TaskSerializer

    def get_project_id_or_error(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'parameter project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        return project_id

    def assign_user(self, request, pk):
        instance = self.get_object()

        previous_assignee = instance.assignee

        response = check_permission(self.request.user, instance.project_id)

        if response:
            return response

        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        assignee_id = request.data['assignee']

        if previous_assignee and previous_assignee.id == assignee_id:
            return Response({'message': 'Assignee is already assigned to this task'})

        if assignee_id:

            assignee = get_user_model().objects.filter(id=assignee_id).first()

            is_project_member = Member.objects.filter(
                user=assignee, project_id=instance.project_id).exists()

            if not is_project_member:
                return Response({
                    'error': 'Assignee is not a member of this project'
                })

        serializer.save(assignee=assignee)

        if assignee_id and assignee != request.user:
            user_full_name = f"{request.user.first_name} {request.user.last_name}"

            Notification.objects.create(
                recipient=assignee,
                message=f"Task '{instance.title}' has been assigned to you by {user_full_name}."
            )

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            response = check_permission(
                self.request.user, serializer.validated_data['project'])

            if response:
                return response

            serializer.save()
            return Response({
                'status': 'Successful'
            }, status=status.HTTP_201_CREATED)
        else:
            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
            return Response(new_error, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        project_id = self.get_project_id_or_error(request)

        if isinstance(project_id, Response):
            return project_id

        response = check_permission(self.request.user, project_id)

        if response:
            return response

        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        response = check_permission(self.request.user, instance.project_id)

        if response:
            return response

        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)

        return instance

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)

        if self.action == 'list':
            project_id = self.get_project_id_or_error(self.request)
            if isinstance(project_id, Response):
                return project_id

            queryset = queryset.filter(
                project=project_id, project__members__user=self.request.user)

            assignee_ids = self.request.query_params.getlist('assignee_ids')
            if assignee_ids:
                assignee_ids = [int(id) for id in assignee_ids]
                queryset = queryset.filter(assignee__id__in=assignee_ids)

        else:
            pk = self.kwargs.get('pk')
            queryset = queryset.filter(pk=pk)

        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        response = check_permission(request.user, instance.project_id)

        if response:
            return response

        request.data.pop('assignee', None)

        updated_fields = []

        for key, value in request.data.items():
            current_val = getattr(instance, key, None)
            if current_val and value != current_val:
                updated_fields.append(key)

        if updated_fields:
            user_full_name = f'{request.user.first_name} {request.user.last_name}'

            message = f'{user_full_name} updated the following [{", ".join(updated_fields)}] in the Task `{instance.title}`'

            if instance.created_by == request.user:
                Notification.objects.create(
                    recipient=instance.created_by,
                    message=message
                )

            return super().update(request, *args, **kwargs)

        return Response({
            'message': 'The request did not contain any changes. Task remains unchanged.'
        })

    def delete(self, request):
        project_id = self.get_project_id_or_error(request)

        if isinstance(project_id, Response):
            return project_id

        response = check_permission(self.request.user, project_id)

        if response:
            return response

        return super().destroy(request)
