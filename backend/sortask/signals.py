from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Task, Notification


@receiver(post_save, sender=Task)
def task_updated(sender, instance, created, **kwargs):
    if created or instance.has_changes():  # Check for significant changes if needed
        if instance.assignee:
            notification = Notification.objects.create(
                user=instance.assignee,
                task=instance,
                message=f"Task '{instance.title}' has been updated."
            )
            async_to_sync(get_channel_layer().group_send)(
                f"notifications_{instance.assignee.id}", {
                    'type': 'send_notification',
                    'message': notification.message,
                }
            )
