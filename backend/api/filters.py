from django.contrib.auth import get_user_model
from django_filters import NumberFilter
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipes

User = get_user_model()


class IngredientsFilter(SearchFilter):
    """
    Полнотекстовый поиск по ингредиентам
    !НО не сделал еще игнорирование регистра
    """

    def get_search_fields(self, view, request):
        if request.query_params.get('name'):
            return ['name']
        return super().get_search_fields(view, request)

    search_param = 'name'


class RecipesFilterSet(FilterSet):
    """Фильтр рецептов по тегам, авторам, избранному, подпискам"""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_shopping_cart')

    def filter_is_favorited(self, queryset, is_favorited, number):
        """Фильтрация по избранному"""

        user = self.request.user
        if number == 1:
            return queryset.filter(favorite_related__user=user)
        return queryset.exclude(favorite_related__user=user)

    def filter_shopping_cart(self, queryset, is_in_shopping_cart, number):
        """Фильтрация по списку покупок"""

        user = self.request.user
        if number == 1:
            return queryset.filter(cart_related__user=user)
        return queryset.exclude(cart_related__user=user)

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
