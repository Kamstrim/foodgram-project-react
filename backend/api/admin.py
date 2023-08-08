from django.contrib import admin

from .models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)


admin.site.register(Follow)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
