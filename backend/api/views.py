from io import BytesIO

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientsFilter, RecipesFilterSet
from api.permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientsSerializer,
                             RecipesSerializer, ShortSerializer,
                             SubscribeSerializer, TagsSerializer)
from recipes.models import (Cart, Favorite, IngredientInRecipe, Ingredients,
                            Recipes, Tags)
from users.models import Subscribe

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User и Subscribe"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminAuthorOrReadOnly]
    pagination_class = PageNumberPagination

    @action(
        methods=['get'], detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=PageNumberPagination
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
    """Вьюсет для модели Recipes, Favorite и Cart"""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_class = RecipesFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    def favorite_and_cart(self, request, pk, model, errors):
        """Общая функция для Favorite и Cart для добавления и удаления"""

        user = request.user
        obj = model.objects.filter(user=user, recipe=pk)
        if request.method == 'POST':
            if obj.exists():
                return Response(
                    {'errors': errors.get('if_exists')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipes, id=pk)
            model.objects.create(user=user, recipe=recipe)
            return Response(
                ShortSerializer(recipe).data, status=status.HTTP_201_CREATED
            )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': errors.get('if_deleted')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Функция добавления и удаления избранного."""

        errors = {
            'if_exists': 'Рецепт уже добавлен в избранное',
            'if_deleted': 'Вы уже удалили рецепт из избранного'
        }

        return self.favorite_and_cart(request, pk, Favorite, errors)

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Функция добавления и удаления рецептов в/из списка покупок."""

        errors = {
            'if_exists': 'Рецепт уже добавлен в список покупок',
            'if_deleted': 'Вы уже удалили рецепт из списка покупок'
        }

        return self.favorite_and_cart(request, pk, Cart, errors)

    @action(
        methods=['get'], detail=False, permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в pdf"""

        ingredients = IngredientInRecipe.objects.filter(
            recipe__cart_related__user=request.user).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit',
            'recipe__name'
        )
        if ingredients:
            ingredient_dict = {}
            for ingredient_name, amount, unit, recipe_name in ingredients:
                if ingredient_name not in ingredient_dict:
                    ingredient_dict[ingredient_name] = {
                        'amount': amount,
                        'measurement_unit': unit,
                        'recipe_name': recipe_name
                    }
                else:
                    ingredient_dict[ingredient_name]['amount'] += amount

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = (
                'inline; filename="shopping_list.pdf"'
            )

            buffer = BytesIO()
            page = canvas.Canvas(buffer)

            pdfmetrics.registerFont(
                TTFont(
                    'Roboto-Regular',
                    'recipes/static/fonts/Roboto-Regular.ttf', 'UTF-8'
                )
            )
            page.setFont('Roboto-Regular', size=24)
            page.drawString(150, 800, 'Рецепты с сайта Foodgram')
            page.setFont('Roboto-Regular', size=20)
            page.drawString(130, 750, 'Список ингредиентов для рецептов')
            page.setFont('Roboto-Regular', size=16)
            height = 700
            for ingredient_name, info in ingredient_dict.items():
                page.drawString(
                    50, height, f'• {ingredient_name} - {info["amount"]} '
                                f'{info["measurement_unit"]} для рецепта: '
                                f'{info["recipe_name"]}.'
                )
                height -= 20

            page.showPage()
            page.save()
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            return response

        return Response(
            {'errors': 'Нет рецептов в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )
