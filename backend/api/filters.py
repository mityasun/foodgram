from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipes

User = get_user_model()


class IngredientsFilter(SearchFilter):
    """Полнотекстовый поиск по ингредиентам"""

    def get_search_fields(self, view, request):
        if request.query_params.get('name'):
            return ['name']
        return super().get_search_fields(view, request)

    search_param = 'name'


class TagsAuthorFilterSet(FilterSet):
    """Фильтр рецептов по тегам и авторам"""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipes
        fields = ('tags', 'author')
