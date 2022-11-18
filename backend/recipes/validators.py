import re

from django.core.exceptions import ValidationError


def validate_slug(slug):
    """Валидатор slug тегов."""

    pattern = re.compile(r'^[-a-zA-Z0-9_]+')

    if pattern.fullmatch(slug) is None:
        match = re.split(pattern, slug)
        symbol = ''.join(match)
        raise ValidationError(f'Некорректные символы в slug: {symbol}')
    return slug


def validate_cooking_time(cooking_time):
    """Валидатор времени приготовления."""
    if cooking_time < 1:
        raise ValidationError(
            'Время приготовления не может быть меньше 1 мин.'
        )
    return cooking_time


def validate_amount(amount):
    """Валидатор количества ингредиентов."""

    if amount < 1:
        raise ValidationError(
            'Количество ингредиента не может быть меньше одного.'
        )
    return amount
