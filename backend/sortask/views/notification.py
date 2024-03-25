from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import Notification
from ..serializers import NotificationSerializer


class NotificationAPIView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        user = request.user
        notifications = user.notifications.order_by('-timestamp')

        page = self.paginate_queryset(notifications, request, view=self)

        if page:
            serializer = NotificationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data)

    def patch(self, request, id=None):
        if id:
            notification = Notification.objects.filter(id=id).first()

            if not notification:
                return Response({"detail": "Not found."})

            is_read = request.data.get('is_read', None)

            if is_read:
                notification.is_read = is_read
                notification.save()

            return Response(NotificationSerializer(notification).data)

        else:
            user = request.user
            user.notifications.update(is_read=True)
            return Response({'status': 'success', 'message': 'All notifications marked as read'})
