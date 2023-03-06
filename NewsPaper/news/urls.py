from django.urls import path
from .views import NewsList, NewsDetail, PostSearch, NewsCreate, NewsUpdate, NewsDelete, ArticleCreate, ArticleDelete, ArticleUpdate, IndexView, CategoryListView
from .views import upgrade_me, subscribe


urlpatterns = [
   path('', NewsList.as_view(), name='news'),
   path('<int:pk>', NewsDetail.as_view(), name='news_item'),
   path('search/', PostSearch.as_view(), name='post_search'),

   path('news/create/', NewsCreate.as_view(), name='news_create'),
   path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_create'),
   path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),

   path('article/create/', ArticleCreate.as_view(), name='article_create'),
   path('article/<int:pk>/edit/', ArticleUpdate.as_view(), name='news_create'),
   path('article/<int:pk>/delete/', ArticleDelete.as_view(), name='news_delete'),

   path('upgrade/', upgrade_me, name='upgrade'),

   path('personal/', IndexView.as_view(), name='personal_stuff'),

   path('categories/<int:pk>/', CategoryListView.as_view(), name='category_list'),
   path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
]
