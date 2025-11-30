from django.urls import path
from .views import (
    NotificationListView,
    UnreadNotificationListView,
    NotificationDetailView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    DeleteNotificationView,
    NotificationCountView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread/', UnreadNotificationListView.as_view(), name='unread-notifications'),
    path('count/', NotificationCountView.as_view(), name='notification-count'),
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-read'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('<int:pk>/delete/', DeleteNotificationView.as_view(), name='delete-notification'),
]