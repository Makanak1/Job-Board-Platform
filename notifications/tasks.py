from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

@shared_task
def send_async_email(subject, message, recipient_list, html_message=None):
    """
    Send email asynchronously using Celery
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@shared_task
def send_bulk_notifications(user_ids, notification_type, title, message):
    """
    Send bulk notifications to multiple users
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    users = User.objects.filter(id__in=user_ids)
    notifications = [
        Notification(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message
        )
        for user in users
    ]
    
    Notification.objects.bulk_create(notifications)
    return len(notifications)

@shared_task
def cleanup_old_notifications():
    """
    Delete old read notifications (older than 30 days)
    """
    from django.utils import timezone
    from datetime import timedelta
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    deleted_count = Notification.objects.filter(
        is_read=True,
        created_at__lt=thirty_days_ago
    ).delete()[0]
    
    return deleted_count