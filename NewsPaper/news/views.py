from datetime import datetime
from django.urls import reverse_lazy, resolve
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category, PostCategory
from .filters import PostFilter
from .forms import PostForm
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from .tasks import notify_about_new_post


# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string



class NewsList(ListView):
    model = Post
    ordering = '-time_created'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    # пусть оно просто будет здесь, закомментированное
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     self.filterset = PostFilter(self.request.GET, queryset)
    #     return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        # пусть это пока побудет здесь, вдруг пригодится
        # context['next_news'] = "Тут что-то должно быть написано. Зачем оно? Пусть будет!"
        context['news_number'] = Post.objects.all()
        # context['filterset'] = self.filterset
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_item.html'
    context_object_name = 'news_item'


class PostSearch(ListView):
    model = Post
    ordering = '-time_created'
    template_name = 'post_search.html'
    context_object_name = 'post_search'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_number'] = Post.objects.all()
        context['filterset'] = self.filterset
        return context


class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_create.html'

    permission_required = ('news.add_post',
                           'news.change_post')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NE'

#         notify_about_new_post.delay()
        return super().form_valid(form)


class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'news_create.html'

    permission_required = ('news.add_post',
                           'news.change_post')

    def form_valid(self, form):
        post = form.save(commit=False)
        if post.post_type == 'AR':
            return HttpResponse('Такой новости не существует.')
        post.save()
        return super().form_valid(form)

    # изначально в задании стояло добавить кнопку стать автором, но под конец это стало нелогично
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
    #     return context


class NewsDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news')


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'article_create.html'

    permission_required = ('news.add_post',
                           'news.change_post')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        return super().form_valid(form)


class ArticleUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'article_create.html'

    permission_required = ('news.add_post',
                           'news.change_post')


    def form_valid(self, form):
        post = form.save(commit=False)
        if post.post_type == 'NE':
            return HttpResponse('Такой статьи не существует.')
        post.save()
        return super().form_valid(form)


class ArticleDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'article_delete.html'
    success_url = reverse_lazy('news')


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/posts')


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'personal_stuff.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class CategoryListView(ListView):
    model = Post
    template_name = 'categories.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.categories = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(categories=self.categories).order_by('-time_created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.categories.subscribers.all()
        context['category'] = self.categories
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку новостей категории'
    return render(request, 'subscribe.html', {'category': category, 'message': message})




