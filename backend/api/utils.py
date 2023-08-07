from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .models import Ingredient, RecipeIngredient


def create_model_instance(request, instance, serializer_name):
    """Добавления рецепта в избранное или в список покупок."""

    serializer = serializer_name(
        data={
            'user': request.user.id,
            'recipe': instance.id
        },
        context={
            'request': request
        })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_name, instance, error_message):
    """Удаление рецепта из избранного или из списка покупок."""

    model_instances = request.user.model_name.filter(
        recipe=instance
    )

    if not model_instances.exists():
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    model_instances.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def create_ingredients(ingredients, recipe):
    """Добавление ингредиентов при создании и редактировании рецепта."""

    ingredient_list = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=get_object_or_404(
                Ingredient,
                id=ingredient.get('id')),
            amount=ingredient.get('amount')
        )
        for ingredient in ingredients
    ]

    RecipeIngredient.objects.bulk_create(ingredient_list)
