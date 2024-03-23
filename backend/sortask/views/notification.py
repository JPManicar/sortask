from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Notification
from ..serializers import NotificationSerializer


class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = user.notifications.order_by('-timestamp')

        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data)

    def patch(self, request, id):
        notification = Notification.objects.filter(id=id).first()

        if not notification:
            return Response({"detail": "Not found."})

        is_read = request.data.get('is_read', None)

        if is_read:
            notification.is_read = is_read
            notification.save()

        return Response(NotificationSerializer(notification).data)
