"""

    @ File: serializers.py
    @ Date: 10.03.2023
    @ Author: Ohlupin Maxim

"""
from rest_framework.serializers import Serializer
from rest_framework.serializers import ModelSerializer

from tags.serializers import TagSerializer
from users.serializers import UserSerializer

from .models import Recipe
from .models import Ingredient


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(many=False)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients',  # 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )
