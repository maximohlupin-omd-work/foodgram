from django.db import models

from tags.models import Tag

from users.models import User

from .validators import more_zero_validator


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единицы измерения'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[more_zero_validator, ]
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(verbose_name='Ссылка на картинку на сайте')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[more_zero_validator, ]
    )

    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    author = models.OneToOneField(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='recipe',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
