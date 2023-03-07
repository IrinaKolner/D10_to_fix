import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# пон 8 по Москве - это 5 UTC
app.conf.beat_schedule = {
    'send_all_week_posts_every_monday_8am': {
        'task': 'news.tasks.all_week_posts',
        'schedule': crontab(hour=5, minute=0, day_of_week='monday'),
#         'schedule': crontab(hour=18, minute=47, day_of_week='sunday'),
        'args': (),
    },
}
