from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from news.resources import *
from django.urls import reverse

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group



class Author(models.Model):
    user_rating = models.FloatField(default=0.0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_rating(self):
        author_all_articles_rating = self.post_set.all().aggregate(Sum('post_rating'))['post_rating__sum'] * 3
        author_all_comments_rating = self.user.comment_set.all().aggregate(Sum('comment_rating'))['comment_rating__sum']
        all_comments_to_author_articles_rating = self.post_set.all().aggregate(Sum('comment__comment_rating'))['comment__comment_rating__sum']
        self.user_rating = author_all_articles_rating + author_all_comments_rating + all_comments_to_author_articles_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    culture = 'CU'
    science = 'SC'
    tech = 'TE'
    politics = 'PO'
    sport = 'SP'
    entertainment = 'EN'
    economics = 'EC'
    education = 'ED'

    news_category = models.CharField(unique=True, max_length=2, choices=CATEGORIES)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return self.news_category

    # def __str__(self):
    #     return f'{self.news_category}'

    def get_category(self):
        return self.news_category


class Post(models.Model):
    article = 'AR'
    news = 'NE'

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES)
    time_created = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    post_rating = models.FloatField(default=0.0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def like(self):
        self.likes += 1
        self.save()

    def dislike(self):
        self.dislikes -= 1
        self.save()

    def preview(self):
        return f'{self.text[0:124]}...'

    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return reverse('news_item', args=[str(self.id)])


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_time_created = models.DateTimeField(auto_now_add=True)
    comment_rating = models.FloatField(default=0.0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

    def __str__(self):
        return self.text[:20]


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
