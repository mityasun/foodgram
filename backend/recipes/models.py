from .validators import ValidateSlug
from django.db import models

from backend.settings import TAG_SLUG_NAME, TAG_COLOR, INGREDIENTS


class Ingredients(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENTS, unique=True, db_index=True
    )
    measurement_unit = models.CharField('Ед. измерения', max_length=INGREDIENTS)

    REQUIRED_FIELDS = ['name', 'measurement_unit']

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиенты'
        verbose_name_plural = 'ингредиент'

    def __str__(self):
        return self.name


class Tags(models.Model, ValidateSlug):
    name = models.CharField(
        'Название тега', max_length=TAG_SLUG_NAME, unique=True
    )
    color = models.CharField('Цвет', max_length=TAG_COLOR, null=True)
    slug = models.SlugField(
        'Ссылка',
        max_length=TAG_SLUG_NAME,
        unique=True, null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тэг'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name
