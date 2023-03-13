from django.db import models
from django.core.validators import MinValueValidator

from tags.models import Tag

from users.models import User


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(verbose_name='Ссылка на картинку на сайте')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, message="Время не может быть меньше 1")
        ],
    )

    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единицы измерения'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message="Должен быть больше единицы")
        ],
    )

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Для рецепта",
        related_name="ingredients"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class ShopList(models.Model):
    author = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        related_name="shop_list",
        on_delete=models.CASCADE
    )

    recipes = models.ManyToManyField(
        Recipe,
        verbose_name="Рецепты"
    )

    def __str__(self):
        return f"Список покупок {self.author}"

    class Meta:
        ordering = ('-id',)
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
