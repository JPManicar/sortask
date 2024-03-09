from django.db import models
from django.contrib.auth import get_user_model
import uuid


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='created_projects')

    def create_default_boards(self):
        Board.objects.bulk_create([
            Board(project=self, name='Backlog'),
            Board(project=self, name='In Progress'),
            Board(project=self, name='Done'),
        ])


class ProjectInvitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)


class Board(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='boards')
    name = models.CharField(max_length=255)


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateTimeField()
    assignee = models.ForeignKey(get_user_model(),
                                 related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CheckList(models.Model):
    content = models.CharField(max_length=255)
    is_completed = models.BooleanField()
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='checklists')


class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Member(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='projects')
