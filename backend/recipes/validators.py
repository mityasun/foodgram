import re

from django.core.exceptions import ValidationError


class ValidateSlug:
    """Валидаторы для username."""

    def validate_slug(self, slug):
        pattern = re.compile(r'^[-a-zA-Z0-9_]+')

        if pattern.fullmatch(slug) is None:
            match = re.split(pattern, slug)
            symbol = ''.join(match)
            raise ValidationError(f'Некорректные символы в slug: {symbol}')
        return slug
