from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Member
from ..serializers import MemberSerializer


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        creator = project.created_by.id

        if creator != self.request.user.id:
            return Response({'error': 'You don\'t have permission to remove a member'})

        if creator == instance.user_id:
            return Response({"error": 'You can\'t remove yourself from a project'}, )

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
