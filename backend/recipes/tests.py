from rest_framework.test import APITestCase
from rest_framework.utils.serializer_helpers import ReturnList

from .models import Ingredient
from .models import IngredientUnit
from .models import Recipe


class RecipeTestCase(APITestCase):
    @classmethod
    def setUp(cls) -> None:
        super().setUpClass()

        cls.recipe_model_fields = [
            x.name for x in getattr(Recipe, '_meta').fields
        ]
