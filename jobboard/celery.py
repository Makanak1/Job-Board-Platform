import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobboard.settings')

app = Celery('jobboard')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')