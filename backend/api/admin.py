from django.contrib import admin

from .models import (
    Follow,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

admin.site.register(Follow)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipe)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
