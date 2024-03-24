from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Comment, Task, Notification
from ..serializers import CommentSerializer, UserFullNameSerializer
from ..permissions import check_permission


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == 'list':
            task_id = self.kwargs['task_pk']
            queryset = queryset.filter(task_id=task_id)

        else:
            queryset = queryset.filter(id=self.kwargs.get('pk'))

        return queryset

    def is_comment_creator(self, request):
        comment_id = self.kwargs.get('pk')
        return Comment.objects.filter(user=request.user, id=comment_id).exists()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_id = kwargs.get('task_pk')
        task = Task.objects.filter(id=task_id).first()

        is_not_member = check_permission(
            request.user, task.project)

        if is_not_member:
            return is_not_member

        serializer.save(task_id=kwargs.get('task_pk'))

        user_full_name = f'{request.user.first_name} {request.user.last_name}'
        recipients = []

        if task.assignee and task.assignee != request.user:
            recipients.append(task.assignee)

        if task.created_by != request.user and task.created_by not in recipients:
            recipients.append(task.created_by)

        if recipients:
            Notification.objects.bulk_create([
                Notification(
                    recipient=recipient, message=f"{user_full_name} commented in `{task.title}`")
                for recipient in recipients
            ])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        is_creator = self.is_comment_creator(request)

        if not is_creator:
            return Response({'error': "You don't have permission to update this project"}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        is_creator = self.is_comment_creator(request)

        if not is_creator:
            return Response({'error': "You don't have permission to update this project"}, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
