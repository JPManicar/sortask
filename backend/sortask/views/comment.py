from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Comment
from ..serializers import CommentSerializer
from ..permissions import check_permission


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_pk']
        return Comment.objects.filter(task_id=task_id)

    def is_comment_creator(self, request):
        comment_id = self.kwargs.get('pk')
        return Comment.objects.filter(user=request.user, id=comment_id).exists()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        is_not_member = check_permission(
            request.user, serializer.data.get('project'))

        if is_not_member:
            return is_not_member

        response = self.is_comment_creator(request.user, kwargs.get('pk'))

        if response:
            return response

        serializer.save(task_id=kwargs.get('task_pk'))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
