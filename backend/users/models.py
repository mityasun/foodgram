from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.settings import EMAIL, FIRST_NAME, LAST_NAME, USERNAME, PASSWORD
from .validators import ValidateUsername


class User(AbstractUser, ValidateUsername):
    email = models.EmailField('Почта', max_length=EMAIL, unique=True)
    username = models.CharField('Никнэйм', max_length=USERNAME, unique=True)
    first_name = models.CharField('Имя', max_length=FIRST_NAME)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME)
    password = models.CharField('Пароль', max_length=PASSWORD)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
