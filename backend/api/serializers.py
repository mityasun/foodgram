from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.mixins import check_request_user
from recipes.models import IngredientInRecipe, Ingredients, Recipes, Tags
from recipes.validators import validate_amount, validate_cooking_time
from users.models import Subscribe, User
from users.validators import ValidateUsername


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Получаем статус подписки на автора"""

        # Тут и ниже разные релэйты, поэтому их не объединить в один
        # Здесь в obj хранится user.id
        if not check_request_user(self):
            return False
        return obj.following.exists()


class CustomUserCreateSerializer(UserCreateSerializer, ValidateUsername):
    """Сериализатор регистрации юзеров"""

    email = serializers.EmailField(
        required=True, max_length=settings.EMAIL,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True, max_length=settings.USERNAME,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(
        required=True, max_length=settings.FIRST_NAME
    )
    last_name = serializers.CharField(
        required=True, max_length=settings.LAST_NAME
    )
    password = serializers.CharField(
        required=True, max_length=settings.PASSWORD
    )

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class ShortSerializer(serializers.ModelSerializer):
    """Сериализатор короткого ответа рецептов для подписок и избранного"""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки"""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """Получаем статус подписки на автора"""

        # Тут и выше разные релэйты, поэтому их не объединить в один
        # Здесь хранится объект user
        return obj.user.follower.exists()

    def get_recipes(self, obj):
        """Получаем рецепты, на которые подписаны и ограничиваем по лимитам"""

        queryset = Recipes.objects.filter(author__following__user=obj.user)
        # queryset = obj.author.recipe_author.values()
        # в таком варианте картинки в null превращаются
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return ShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Считаем рецепты автора, на которого подписан пользователь"""

        return obj.author.recipe_author.count()


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связанной модели ингредиентов и рецептов"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор Recipes для создания, обновления и удаления рецептов"""

    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField(
        required=True, max_length=settings.RECIPE_NAME
    )
    image = Base64ImageField(
        max_length=None, required=True,
        allow_null=False, allow_empty_file=False
    )
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(
        required=True, validators=[validate_cooking_time]
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        """Валидируем ингредиенты и теги"""

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужен хотя бы один ингредиент для рецепта'}
            )
        ingredients_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredients, id=ingredient_item['id']
            )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты не должны повторяться'}
                )
            validate_amount(int(ingredient_item['amount']))
            ingredients_list.append(ingredient)
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужен хотя бы один тэг для рецепта'}
            )
        tags_list = []
        for tag_item in tags:
            tag = get_object_or_404(Tags, id=tag_item)
            if tag in tags_list:
                raise serializers.ValidationError(
                    {'tags': 'Теги в рецепте не должны повторяться'}
                )
            tags_list.append(tag)

        data['author'] = self.context.get('request').user
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data

    def create_ingredients(self, ingredients, recipe):
        """Создаем связку ингредиентов для рецепта"""

        for ingredient_item in ingredients:
            IngredientInRecipe.objects.bulk_create(
                [IngredientInRecipe(
                    ingredient_id=ingredient_item['id'],
                    recipe=recipe,
                    amount=ingredient_item['amount']
                )]
            )

    def create(self, validated_data):
        """Создаем рецепт"""

        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        """Обновляем рецепт"""

        recipe.ingredients.clear()
        self.create_ingredients(validated_data.pop('ingredients'), recipe)
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        recipe.tags.set(tags)
        return recipe

    def delete(self, recipe):
        """Удаляем рецепт"""

        recipe.delete()

    def get_is_favorited(self, obj):
        """Получаем статус избранного"""

        if not check_request_user(self):
            return False
        return Recipes.objects.filter(
            favorite__user=obj.user, id=obj.id
        ).exists()
        # return obj.id.favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """Получаем статус списка покупок"""

        if not check_request_user(self):
            return False
        return Recipes.objects.filter(
            cart__user=obj.user, id=obj.id
        ).exists()
        # return obj.id.cart.exists()
