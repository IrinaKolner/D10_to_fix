from celery import shared_task
import datetime
from django.conf import settings


from news.models import Post, Category, User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives




# я не знаю, как нужно все это переделать, чтобы оно работало
# def send_notifications(preview, pk, title, subscribers):
#     html_content = render_to_string(
#         'post_created_email.html',
#         {
#             'text': preview,
#             'link': f'{settings.SITE_URL}/posts/{pk}'
#             # 'link': f'http://127.0.0.1:8000/posts/{pk}'
#         }
#     )

#     msg = EmailMultiAlternatives(
#         subject=title,
#         body='',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         # from_email='ann.annannanna@yandex.ru',
#         to=subscribers,
#     )

#     msg.attach_alternative(html_content, 'text/html')
#     msg.send()



# @shared_task
# def notify_about_new_post():

#     categories = Category.news_category.all()
#     subscribers: list[str] = []
#     for category in categories:
#         subscribers += category.subscribers.all()

#     subscribers = [s.email for s in subscribers]

#     send_notifications(Post.preview(), Post.pk, Post.title, subscribers)





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

