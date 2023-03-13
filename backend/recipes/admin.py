from django.contrib import admin

from .models import Recipe
from .models import ShopList
from .models import Favorite
from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name',)


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('author',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author',)


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShopList, ShopListAdmin)
