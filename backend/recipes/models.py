from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

from backend.settings import INGREDIENTS, RECIPE_NAME, TAG_COLOR, TAG_SLUG_NAME

from .validators import validate_amount, validate_cooking_time, validate_slug

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENTS, db_index=True
    )
    measurement_unit = models.CharField(
        'Ед. измерения', max_length=INGREDIENTS
    )

    REQUIRED_FIELDS = ['name', 'measurement_unit']

    class Meta:
        ordering = ('id',)
        verbose_name = 'ингредиенты'
        verbose_name_plural = 'ингредиент'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique ingredient'
            )
        ]

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(
        'Название тега', max_length=TAG_SLUG_NAME, unique=True
    )
    color = ColorField('Цвет', format='hex', max_length=TAG_COLOR, unique=True)
    slug = models.SlugField(
        'Ссылка', max_length=TAG_SLUG_NAME,
        unique=True, validators=[validate_slug]
    )

    REQUIRED_FIELDS = ['name', 'color', 'slug']

    class Meta:
        ordering = ('id',)
        verbose_name = 'тэг'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    name = models.CharField('Название рецепта', max_length=RECIPE_NAME)
    text = models.TextField('Описание')
    image = models.ImageField('Картинка', upload_to='recipes/%Y/%m/%d/')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', validators=[validate_cooking_time]
    )
    tags = models.ManyToManyField(Tags, verbose_name='теги')
    ingredients = models.ManyToManyField(
        Ingredients, through='IngredientInRecipe', verbose_name='Ингредиенты'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )

    REQUIRED_FIELDS = [
        'name', 'text', 'image', 'cooking_time',
        'tags', 'ingredients', 'author'
    ]

    class Meta:
        ordering = ('-id',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[validate_amount]
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique ingredient in recipe'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique favorite'
            )
        ]

    def __str__(self):
        return f'Пользователь:{self.user.username}, рецепт: {self.recipe.name}'


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='buyer', verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        related_name='cart', verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique cart'
            )
        ]

    def __str__(self):
        return f'Пользователь:{self.user.username}, рецепт: {self.recipe.name}'
