"""

    @ File: serializers.py
    @ Date: 10.03.2023
    @ Author: Ohlupin Maxim

"""
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from tags.models import Tag
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
    image = serializers.SerializerMethodField()

    def get_image(self, value):
        request = self.context["request"]
        if request.headers.get("Host"):
            real_host = request.headers.get("Host")
            return f"http://{real_host}{value.image.url}"
        return request.build_absolute_uri(value.image.url)

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


class IngredientRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        data.update(
            ingredient_unit=get_object_or_404(
                IngredientUnit, id=data.pop('id')
            )
        )
        return data

    def to_representation(self, value):
        return dict(
            amount=value.amount,
            **IngredientUnitSerializer(value.ingredient_unit).data
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, allow_empty=False, queryset=Tag.objects.all()
    )
    ingredients = IngredientRelatedField(
        many=True, allow_empty=False, queryset=Ingredient
    )

    image = Base64ImageField()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)

        for ingredient in ingredients:
            Ingredient.objects.create(
                recipes=recipe,
                **ingredient
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        new_ids = {x['ingredient_unit'].id for x in ingredients}
        old_ids = {
            x['ingredient_unit__id'] for x in instance.ingredients.values(
                'ingredient_unit__id'
            )
        }

        to_update = new_ids - old_ids
        to_delete = old_ids - new_ids

        instance.ingredients.filter(
            ingredient_unit__id__in=to_delete
        ).delete()

        for ingredient in ingredients:
            _id = ingredient['ingredient_unit'].id
            if _id in to_update:
                curr_ingrid = instance.ingredients.filter(id=_id)
                if curr_ingrid.exists():
                    curr_ingrid = curr_ingrid.first()
                    curr_ingrid.amount = ingredient['amount']
                    curr_ingrid.save()
                else:
                    Ingredient.objects.create(
                        recipes=instance,
                        **ingredient
                    )
        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = '__all__'
