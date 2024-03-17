from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Project, ProjectInvitation, Board, Task, CheckList, Comment, Member
from typing import Optional, List


class CheckListSerializer(serializers.ModelSerializer):
    is_completed = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = CheckList
        fields = ['is_completed', 'content']


class CommentSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=get_user_model().objects.all())

    class Meta:
        model = Comment
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=get_user_model().objects.all())

    checklists = CheckListSerializer(many=True)

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()  # Limit allowed boards
    )

    assignee = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False)

    class Meta:
        model = Task
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')  # Access the request object

        if not request:
            return

        assignee = request.data.get('assignee')
        project = request.data.get('project')

        if not assignee or not project:
            return

        has_permission = Member.objects.filter(
            user_id=assignee, project_id=project).exists()

        if not has_permission:
            raise serializers.ValidationError(
                {"assignee": "Assigned user is not a member of the project."})

    def validate(self, data):
        project = data.get('project')
        board = data.get('board')
        if project and board:
            if board.project != project:
                raise serializers.ValidationError(
                    'Board must belong to the assigned project.')
        return data

    def create(self, validated_data):
        checklists_data = validated_data.pop('checklists', [])
        task = Task.objects.create(**validated_data)
        for checklist in checklists_data:
            CheckList.objects.create(task=task, **checklist)
        return task

    def update(self, instance, validated_data):
        checklists_data = validated_data.pop('checklists', [])

        instance.checklists.all().delete()

        # Update or create checklists
        for checklist_data in checklists_data:
            CheckList.objects.update_or_create(
                id=checklist_data.get('id'), task=instance, defaults=checklist_data
            )

        instance = super().update(instance, validated_data)

        return instance


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'board', 'assignee']


class BoardAndTaskSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'tasks']


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = ['id', 'name']


class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=get_user_model().objects.all())

    boards = BoardAndTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvitation
        fields = ['token']


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title']


class UserFullNameSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    class Meta:
        model = get_user_model()
        fields = ['id', 'full_name']


class MemberSerializer(serializers.ModelSerializer):
    user = UserFullNameSerializer(read_only=True)

    class Meta:
        model = Member
        fields = '__all__'
