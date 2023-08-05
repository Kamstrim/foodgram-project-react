from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

User = get_user_model()

LIMIT_ING_NAME = 200
LIMIT_ING_UNIT = 200
LIMIT_TAG_NAME = 200
LIMIT_TAG_COLOR = 7
LIMIT_TAG_SLUG = 200
LIMIT_RECIPE_NAME = 200
REGEX = r'^[-a-zA-Z0-9_]+$'


class Ingredient(models.Model):
    """Модель Ингридиента."""

    name = models.CharField(
        max_length=LIMIT_ING_NAME,
        verbose_name='название ингридиента',
    )

    measurement_unit = models.CharField(
        max_length=LIMIT_ING_UNIT,
        verbose_name='мера измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'ингридиент'
        verbose_name_plural = 'игридиенты'

    def __str__(self):
        return f'{self.name} -> {self.measurement_unit}'


class Tag(models.Model):
    """Модель Тега."""

    name = models.CharField(
        max_length=LIMIT_TAG_NAME,
        unique=True,
        verbose_name='название тега',
    )

    color = models.CharField(
        max_length=LIMIT_TAG_COLOR,
        verbose_name='цвет в HEX',
        unique=True,
    )

    slug = models.SlugField(
        max_length=LIMIT_TAG_SLUG,
        validators=[RegexValidator(REGEX)],
        unique=True,
        verbose_name='уникальный слаг',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='ингредиенты',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги',
    )

    name = models.CharField(
        max_length=LIMIT_RECIPE_NAME,
        verbose_name='название рецепта',
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='изображение',
    )

    text = models.TextField(
        verbose_name='описание',
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Должно быть больше 1')
        ],
        verbose_name='время приготовления',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингредиентов рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Должно быть больше 1')
        ],
        verbose_name='количество',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} -> '
            f'{self.ingredient.measurement_unit} -> '
            f'{self.amount}'
        )


class FavoriteRecipe(models.Model):
    """Модель Избранный Рецепт."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='автор рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        ]
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    """Модель Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='автор списка',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_hopping_list',
            ),
        ]
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Follow(models.Model):
    """Подписка на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name='подписик',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='автор',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_self_follow'
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.author}"
