"""

    @ File: serializers.py
    @ Date: 10.03.2023
    @ Author: Ohlupin Maxim

"""
from rest_framework import serializers

from tags.serializers import TagSerializer
from users.serializers import UserSerializer

from .models import Recipe
from .models import Ingredient
from .models import IngredientUnit


class IngredientUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientUnit
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    ingredient_unit = IngredientUnitSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        unit = data.pop('ingredient_unit')
        unit.pop('id')
        data.update(**unit)
        return data

    class Meta:
        model = Ingredient
        fields = (
            'id', 'ingredient_unit', 'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(many=False)
    ingredients = IngredientSerializer(many=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )
    is_favorited = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_in_shopping_cart', 'is_favorited',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
