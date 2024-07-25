from django.db import models


class ShortLink(models.Model):
    full_url = models.TextField(
        unique=True,
        verbose_name='Полная ссылка',
        help_text='Обязательное поле'
    )
    short_link = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name='Короткая ссылка',
        help_text=('Обязательное поле, '
                   'несмотря на то что может быть пустым')
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f's/{self.short_link} ведет на {self.full_url}'
