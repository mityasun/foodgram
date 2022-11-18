from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientsFilter, TagsAuthorFilterSet
from api.permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientsSerializer,
                             RecipesSerializer, ShortSerializer,
                             SubscribeSerializer, TagsSerializer)
from recipes.models import Favorite, Ingredients, Recipes, Tags
from users.models import Subscribe

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User и Subscribe"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    @action(
        methods=['get'], detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        """Получить подписки пользователя"""

        serializer = SubscribeSerializer(
            self.paginate_queryset(
                Subscribe.objects.filter(user=request.user)
            ), many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Функция подписки и отписки."""

        user = request.user
        author = get_object_or_404(User, pk=id)
        subscribe_obj = Subscribe.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if user == author:
                return Response({'errors': 'На себя подписаться нельзя'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            if subscribe_obj.exists():
                return Response(
                    {'errors': f'Вы уже подписаны на {author.username}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=user, author=author),
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if user == author:
            return Response(
                {'errors': 'Вы не можете отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if subscribe_obj.exists():
            subscribe_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Вы уже отписались от {author.username}'},
            status=status.HTTP_400_BAD_REQUEST
        )


class IngredientsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для модели Ingredients"""

    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = (IngredientsFilter,)


class TagsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для модели Tags"""

    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class RecipesViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Вьюсет для модели Recipes и Favorite"""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_class = TagsAuthorFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Функция добавления и удаления из избранного."""

        user = request.user
        favorite_obj = Favorite.objects.filter(user=user, recipe=pk)

        if request.method == 'POST':
            if favorite_obj.exists():
                return Response({'errors': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            recipe = get_object_or_404(Recipes, id=pk)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if favorite_obj.exists():
            favorite_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы уже удалили рецепт из избранного'},
            status=status.HTTP_400_BAD_REQUEST
        )
