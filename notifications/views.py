from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer

class NotificationListView(generics.ListAPIView):
    """
    List user notifications
    GET /api/notifications/
    """
    serializer_class = NotificationListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class UnreadNotificationListView(generics.ListAPIView):
    """
    List unread notifications
    GET /api/notifications/unread/
    """
    serializer_class = NotificationListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user, is_read=False)

class NotificationDetailView(generics.RetrieveAPIView):
    """
    Get notification details and mark as read
    GET /api/notifications/{id}/
    """
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class MarkNotificationReadView(APIView):
    """
    Mark notification as read
    POST /api/notifications/{id}/mark-read/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})

class MarkAllNotificationsReadView(APIView):
    """
    Mark all notifications as read
    POST /api/notifications/mark-all-read/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})

class DeleteNotificationView(generics.DestroyAPIView):
    """
    Delete a notification
    DELETE /api/notifications/{id}/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class NotificationCountView(APIView):
    """
    Get unread notification count
    GET /api/notifications/count/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})