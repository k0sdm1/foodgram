from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import (
    EmailValidator,
    RegexValidator
)


MAX_USERNAME_LENGTH = 150
MAX_FIRSTNAME_LENGTH = 150
MAX_LASTNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
USERNAME_REGEX = r'^[\w.@+-\\]+\Z'
FORBIDDEN_USERNAMES = {'me', }


class MyUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        verbose_name='Имя пользователя',
        help_text='Обязательное поле',
        validators=(RegexValidator(USERNAME_REGEX),))
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта',
        help_text='Обязательное поле',
        validators=(EmailValidator,))
    first_name = models.CharField(
        max_length=MAX_FIRSTNAME_LENGTH,
        verbose_name='Имя',
        help_text='Обязательное поле'
    )
    last_name = models.CharField(
        max_length=MAX_LASTNAME_LENGTH,
        verbose_name='Фамилия',
        help_text='Обязательное поле'
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None,
        verbose_name='Аватар пользователя',
        help_text='Необязательно, допустимые форматы: jpg, png'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

        def __str__(self):
            return self.username
