from celery import shared_task
# from django.contrib.auth.models import User
# from django.core.mail import EmailMultiAlternatives
# from django.dispatch import receiver
# from django.db.models.signals import m2m_changed
# from news.models import PostCategory
# from django.template.loader import render_to_string
# from django.conf import settings
#
#
# import logging
import datetime

from django.conf import settings

# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.core.management.base import BaseCommand
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution

from news.models import Post, Category, PostCategory, User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from django.db.models.signals import m2m_changed


# вернуть
def send_notifications(preview, pk, title, subscribers):
    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': preview,
            'link': f'{settings.SITE_URL}/posts/{pk}'
            # 'link': f'http://127.0.0.1:8000/posts/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        # from_email='ann.annannanna@yandex.ru',
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


# первый аргумент - сигнал, т.е., когда событие должно срабатывать
# в данном случае - m2m_changed - он срабатывает, когда мы в статью добавляем категорию
# т.е. когда создаем статью и определяем ее категорию
# sender - та модель, которая только что была изменена
@shared_task
def notify_about_new_post():

    categories = Category.news_category.all()
    subscribers: list[str] = []
    for category in categories:
        subscribers += category.subscribers.all()

    subscribers = [s.email for s in subscribers]

        # send_notifications - эта функция и будет отправлять сообщения (она находится выше)
    send_notifications(Post.preview(), Post.pk, Post.title, subscribers)




# использовала тот же шаблон, что и для apscheduler
@shared_task
def all_week_posts():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_created__gte=last_week)
    categories = set(posts.values_list('categories__news_category', flat=True))
    subscribers = set(Category.objects.filter(news_category__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,

        }
    )
    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
# NB изначально я хотела отправлять рассылку всем пользователям (чтобы не дублировать apscheduler,
# но в таком случае выдавало ошибку, так как у меня сть пользователи без почты
