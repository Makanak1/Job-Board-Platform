from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('recipient', 'created_at')

class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'notification_type', 'title', 'message', 'link', 
                'is_read', 'created_at')