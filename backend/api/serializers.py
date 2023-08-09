from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from users.models import LIMIT_USERNAME, REGEX

from .models import (MAX_VALUE, MIN_VALUE, FavoriteRecipe, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from .utils import create_ingredients

User = get_user_model()


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" запрещено'
        )
    return value


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    username = serializers.RegexField(
        max_length=LIMIT_USERNAME,
        required=True,
        regex=REGEX
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )

    def validate_username(self, value):
        if User.objects.filter(
                username=value
        ).exists():
            raise serializers.ValidationError(
                'Пользователь c данным Username уже существует'
            )
        return validate_username(value)


class CustomUserSerializer(UserSerializer):
    """Серилизатор для кастомной модели пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        abstract = True
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class SubscribeListSerializer(CustomUserSerializer):
    """Серилизатор подписок пользователя."""

    recipes_count = serializers.SerializerMethodField()
    recipes = SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count',
            'recipes',
            'is_subscribed'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(
            User,
            id=author_id
        )
        user = self.context.get('request').user
        if user.follower.filter(
                author=author_id
        ).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', settings.LIMIT_DEFAULT)
        recipes = obj.recipes.all()[:int(limit)]
        serializer = RecipeShortSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            following = obj.following.filter(
                user=request.user
            ).exists()
            return following
        return False

    def to_representation(self, instance):
        self.fields['is_subscribed'].context = self.context
        return super().to_representation(instance)

    def to_internal_value(self, data):
        """Переопределение метода для передачи дополнительного контекста."""
        return super().to_internal_value({
            **data,
            'request': self.context.get('request')
        })


class TagsSerializer(serializers.ModelSerializer):
    """Сериализация тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов при работе с рецептами."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        max_value=MIN_VALUE,
        min_value=MAX_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор связи инредиента и рецепта."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )

class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов."""

    tags = TagsSerializer(
        read_only=False,
        many=True)
    author = CustomUserSerializer(
        read_only=True,
        many=False)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_recipe(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(
            ingredients,
            many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.favorite_recipe.filter(
                    user=request.user
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.shopping_list.filter(
                    user=request.user
                ).exists())


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    ingredients = IngredientPostSerializer(
        many=True,
        source='recipeingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        max_value=MIN_VALUE,
        min_value=MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_tags(self, tags):
        if not all(Tag.objects.filter(id=tag.id).exists() for tag in tags):
            raise serializers.ValidationError(
                'Указанного тега не существует')
        return tags

    def validate_recipeingredients(self, recipeingredients):
        ingredients_list = [
            ingredient.get('id')
            for ingredient in recipeingredients
        ]
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                'Вы пытаетесь добавить в рецепт два одинаковых ингредиента'
            )
        return recipeingredients

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = request.user.recipes.create(
            **validated_data
        ).create
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.recipeingredients.all().delete()
        super().update(instance, validated_data)
        create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance,
            context={'request': request}
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для полей избранных рецептов и покупок."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = FavoriteRecipe
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        user = data['user']
        if user.favorite_recipe.filter(
                recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(
                recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data
