from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from ..models import Member
from ..serializers import MemberSerializer
from ..permissions import check_permission
import django_filters


class MemberFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(
        field_name='user__email', lookup_expr='icontains')
    name = django_filters.CharFilter(method='filter_by_full_name')

    class Meta:
        model = Member
        fields = ['email', 'name']

    def filter_by_full_name(self, queryset, name, value):
        return queryset.annotate(
            full_name=Concat(
                'user__first_name', Value(' '), 'user__last_name', output_field=CharField())
        ).filter(full_name__icontains=value)


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MemberFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)

        if self.action == 'list':
            project_id = self.kwargs['project_pk']
            queryset = queryset.filter(project_id=project_id)

        else:
            queryset = queryset.filter(id=self.kwargs.get('pk'))

        return queryset

    def retrieve(self, request, project_pk, pk):
        response = check_permission(self.request.user, project_pk)

        if response:
            return response

        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

    def list(self, request, project_pk):
        response = check_permission(self.request.user, project_pk)

        if response:
            return response

        page = self.paginate_queryset(queryset=self.get_queryset())

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

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
