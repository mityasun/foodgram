from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from backend.settings import RECIPE_NAME
from recipes.models import Tags, Ingredients, Recipes, IngredientInRecipe
from recipes.validators import validate_cooking_time, validate_amount
from users.models import User
from users.validators import ValidateUsername


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User"""

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class CustomUserCreateSerializer(UserCreateSerializer, ValidateUsername):
    """Сериализатор регистрации юзеров"""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


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
        lookup_field = ['name']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связанной модели ингредиентов и рецептов"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор Recipes для создания и обновления рецептов"""

    name = serializers.CharField(required=True, max_length=RECIPE_NAME)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(
        required=True, validators=[validate_cooking_time]
    )
    image = Base64ImageField(
        max_length=None, required=True,
        allow_null=False, allow_empty_file=False
    )
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True, read_only=True
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'id', 'name', 'text', 'cooking_time', 'image', 'tags',
            'ingredients', 'author'
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
            ingredient_list.append(ingredient)
            validate_amount(ingredient_item['amount'])
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
