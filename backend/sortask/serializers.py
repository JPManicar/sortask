from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectInvitation, Board, Task, CheckList, Comment, Member
from typing import Optional, List


class CheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=get_user_model().objects.all())

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()  # Limit allowed boards
    )

    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, data):
        project = data.get('project')
        board = data.get('board')
        if project and board:
            if board.project != project:
                raise serializers.ValidationError(
                    'Board must belong to the assigned project.')
        return data


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


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
