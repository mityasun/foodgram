from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.permissions import IsAdminOrReadOnly
from api.serializers import TagsSerializer, IngredientsSerializer
from recipes.models import Tags, Ingredients


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tags"""

    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    # lookup_field = 'name'


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tags"""

    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'name'
