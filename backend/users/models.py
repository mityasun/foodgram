from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import ValidateUsername


class User(AbstractUser, ValidateUsername):
    email = models.EmailField('Почта', max_length=settings.EMAIL, unique=True)
    username = models.CharField(
        'Никнэйм', max_length=settings.USERNAME, unique=True
    )
    first_name = models.CharField('Имя', max_length=settings.FIRST_NAME)
    last_name = models.CharField('Фамилия', max_length=settings.LAST_NAME)
    password = models.CharField('Пароль', max_length=settings.PASSWORD)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='cant subscribe to yourself',
            ),
        ]

    def __str__(self):
        return (
            f'Подписчик: {self.user.username}, Автор: {self.author.username}'
        )
