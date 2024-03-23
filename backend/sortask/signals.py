from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification
from .serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    serializer = NotificationSerializer(instance)
    async_to_sync(get_channel_layer().group_send)(
        f"notifications_{instance.recipient.id}", {
            'type': 'send_notification',
            'data': serializer.data
        }
    )
