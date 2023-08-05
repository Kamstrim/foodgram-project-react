from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

REGEX = r'^[\w.@+-]+\z'
LIMIT_USERNAME = 150
LIMIT_FIRST_NAME = 150
LIMIT_LAST_NAME = 150
LIMIT_PASSWORD = 150
LIMIT_EMAIL = 254


class CustomUser(AbstractUser):
    """Кастомизация модели User."""

    username = models.CharField(
        max_length=LIMIT_USERNAME,
        unique=True,
        verbose_name='username',
    )

    email = models.EmailField(
        max_length=LIMIT_EMAIL,
        unique=True,
        verbose_name='email',
    )

    first_name = models.CharField(
        max_length=LIMIT_FIRST_NAME,
        verbose_name='first_name',
    )

    last_name = models.CharField(
        max_length=LIMIT_LAST_NAME,
        verbose_name='last_name',
    )

    password = models.CharField(
        max_length=LIMIT_PASSWORD,
        verbose_name='password',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
