from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Comment, Task
from ..serializers import CommentSerializer
from ..permissions import check_permission


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.none()

        if self.action == 'list':
            task_id = self.kwargs['task_pk']
            queryset = queryset.union(Comment.objects.filter(task_id=task_id))

        else:
            queryset = queryset.union(
                Comment.objects.filter(id=self.kwargs.get('pk')))

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
