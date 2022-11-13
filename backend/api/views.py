from rest_framework import filters, viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination

from api.permissions import IsAdminOrReadOnly, IsAdminAuthorOrReadOnly
from api.serializers import (TagsSerializer, IngredientsSerializer,
                             RecipesSerializer)
from recipes.models import Tags, Ingredients, Recipes


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tags"""

    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tags"""

    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipesViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Вьюсет для модели Recipes"""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
