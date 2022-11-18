import re

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class ValidateUsername:
    """Валидаторы для username."""

    def validate_username(self, username):
        pattern = re.compile(r'^[\w.@+-]+')

        if pattern.fullmatch(username) is None:
            match = re.split(pattern, username)
            symbol = ''.join(match)
            raise ValidationError(f'Некорректные символы в username: {symbol}')
        if username == 'me':
            raise ValidationError('Ник "me" нельзя регистрировать!')
        return username


class ValidatePassword:
    """Валидаторы пароля от Django."""

    def validate_password(self, password):
        password_validation.validate_password(password)
        return password
