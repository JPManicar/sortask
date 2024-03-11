from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectInvitation, Board, Task, CheckList, Comment, Member


class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=get_user_model().objects.all())

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


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name']


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

    def validate_board(self, value):
        if not value:
            raise serializers.ValidationError("A board is required")

        task = self.instance
        project = getattr(task, 'project', None)

        if not project:
            raise serializers.ValidationError(
                "Project information not available")

        if value not in project.boards.all():
            raise serializers.ValidationError(
                "Board does not belong to the project")

        return value


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'board', 'assignee']


class CheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
