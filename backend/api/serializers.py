from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from backend.settings import (EMAIL, FIRST_NAME, LAST_NAME, PASSWORD,
                              RECIPE_NAME, USERNAME)
from recipes.models import IngredientInRecipe, Ingredients, Recipes, Tags
from recipes.validators import validate_amount, validate_cooking_time
from users.models import Subscribe
from users.validators import ValidateUsername

User = get_user_model()


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

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer, ValidateUsername):
    """Сериализатор регистрации юзеров"""

    email = serializers.EmailField(
        required=True, max_length=EMAIL,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True, max_length=USERNAME,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True, max_length=FIRST_NAME)
    last_name = serializers.CharField(required=True, max_length=LAST_NAME)
    password = serializers.CharField(required=True, max_length=PASSWORD)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class ShortSerializer(serializers.ModelSerializer):
    """Сериализатор короткого ответа для подписок и избранного"""

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

        return Subscribe.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Получаем рецепты, на которые подписаны"""

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipes.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Считаем рецепты, на которые подписаны"""

        return Recipes.objects.filter(author=obj.author).count()


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
    # amount = serializers.IntegerField(
    #     required=True, validators=validate_amount
    # )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор Recipes для создания и обновления рецептов"""

    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField(required=True, max_length=RECIPE_NAME)
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
        """Валидируем ингредиенты"""

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Нужен хотя бы один ингредиент для рецепта'
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredients, id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты в рецепте не должны повторяться'
                )
            validate_amount(int(ingredient_item['amount']))
            ingredient_list.append(ingredient)
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        """Создаем связку ингредиентов для рецепта"""

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        """Создаем рецепт"""

        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """Обновляем рецепт"""

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        """Получаем статус избранного"""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipes.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получаем статус списка покупок"""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipes.objects.filter(cart__user=user, id=obj.id).exists()
