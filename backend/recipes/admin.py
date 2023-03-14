from django.contrib import admin

from .models import Recipe
from .models import ShopList
from .models import Favorite
from .models import Ingredient
from .models import IngredientUnit


class IngredientUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient_unit',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name',)


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('author',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShopList, ShopListAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientUnit, IngredientUnitAdmin)
