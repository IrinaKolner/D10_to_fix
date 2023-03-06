from django.forms import DateInput
from django_filters import FilterSet, DateFilter
from .models import Post


class PostFilter(FilterSet):
    time_created = DateFilter(lookup_expr='gt', widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'author__user_id__username': ['icontains'],
       }