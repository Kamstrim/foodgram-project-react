from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend


from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Follow,
)

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientsSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    TagsSerializer,
    CustomUserSerializer, SubscribeListSerializer,
)
from .utils import create_model_instance, delete_model_instance

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет User."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CustomPagination

    def get_object_or_404_by_id(self, id):
        return get_object_or_404(User, pk=id)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = self.get_object_or_404_by_id(pk)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.get_or_create(
                user=user,
                author=author
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            Follow.objects.filter(
                user=user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = CustomUserSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [IngredientFilter]
    search_fields = ['^name']
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.select_related(
        'author').prefetch_related('tags')
    permission_classes = [AuthorPermission]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return CreateRecipeSerializer

    @staticmethod
    def send_message(self, ingredients):
        shopping_list = 'Список покупок:\n'
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}\n"
            )
        response = HttpResponse(
            shopping_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=False,
        methods=['GET'],
    )
    def download_shopping_list(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=self.request.user
        ).order_by(
            'ingredient__name',
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        )
        return self.send_message(ingredients)

    @staticmethod
    def create_model_instance(self, request, recipe, serializer_class):
        context = {'request': request}
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_model_instance(self, request, model_class, recipe, error_message):
        instance = get_object_or_404(
            model_class,
            user=request.user.id,
            recipe=recipe
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)
        error_message = 'Данного рецепта нет в избранном'
        return delete_model_instance(
            request,
            FavoriteRecipe,
            recipe,
            error_message
        )

    @staticmethod
    def shopping_cart(self, request, recipe):
        context = {'request': request}
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def add_to_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.shopping_cart(request, recipe)

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.delete_model_instance(request, ShoppingCart, recipe, 'Данного рецепта нет в корзине')

