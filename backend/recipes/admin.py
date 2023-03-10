from django.contrib import admin

from .models import Recipe
from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
