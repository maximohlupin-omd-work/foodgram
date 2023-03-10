from django.db import models

from django.core.validators import RegexValidator

from colorfield.fields import ColorField


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = ColorField(default='#FF0000', verbose_name='Цвет в HEX')
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        validators=[
            RegexValidator(
                '^[-a-zA-Z0-9_]+$',
                message='Некорректный слаг'
            )
        ]
    )

    def __str__(self):
        return f"Тэг_{self.name}"

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
