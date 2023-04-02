from django.db.models import Exists
from django.db.models import OuterRef

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from users.permissions import IsAuthOrReadOnly

from .models import Recipe
from .models import IngredientUnit

from .serializers import RecipeSerializer
from .serializers import RecipeInSerializer
from .serializers import CreateRecipeSerializer
from .serializers import IngredientUnitSerializer

from .utils import download_csv

AUTH = dict(
    permission_classes=[IsAuthenticated, ],
    authentication_classes=[TokenAuthentication, ]
)


class IngredientUnitViewSet(viewsets.ModelViewSet):
    queryset = IngredientUnit.objects.all()
    serializer_class = IngredientUnitSerializer
    pagination_class = None
    http_method_names = ('get',)

    def get_queryset(self):
        query_params = self.request.query_params

        name_filter = query_params.get('name')
        if name_filter:
            return self.queryset.filter(
                name__icontains=name_filter[0]
            )

        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_queryset(self):
        query_params = self.request.query_params
        queryset = self.queryset
        if self.request.user.is_authenticated:
            current_user = self.request.user
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    current_user.shop_list.recipes.filter(
                        id=OuterRef('id')
                    )
                ),
                is_favorited=Exists(
                    current_user.favorite.recipes.filter(
                        id=OuterRef('id')
                    )
                )
            )

            is_favorited = query_params.get('is_favorited')
            is_in_shopping_cart = query_params.get('is_in_shopping_cart')
            if is_favorited:
                queryset = queryset.filter(
                    is_favorited=bool(int(is_favorited[0]))
                )

            if is_in_shopping_cart:
                queryset = queryset.filter(
                    is_in_shopping_cart=bool(int(is_in_shopping_cart[0]))
                )

        tags = query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags
            )

        author = query_params.get('author')
        if author:
            queryset = queryset.filter(
                author__id=int(author)
            )
        return queryset.distinct()

    @action(
        methods=('post',), detail=False,
        url_path='(?P<recipe_id>[^/.]+)/shopping_cart',
        **AUTH
    )
    def add_in_shop_list(self, request, recipe_id):
        current_user = request.user
        recipe = Recipe.objects.filter(id=recipe_id)
        if recipe.exists():
            shop_list = current_user.shop_list.recipes
            if shop_list.filter(id=recipe_id).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=dict(error='Уже добавлено')
                )
            recipe = recipe.first()
            shop_list.add(recipe)
            serializer = RecipeInSerializer(recipe)
            return Response(
                status=status.HTTP_201_CREATED,
                data=serializer.data
            )
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data=dict(error='Рецепт не найден')
        )

    @add_in_shop_list.mapping.delete
    def remove_from_shop_list(self, request, recipe_id):
        current_user = request.user
        recipe = Recipe.objects.filter(id=recipe_id)
        if recipe.exists():
            shop_list = current_user.shop_list.recipes
            if shop_list.filter(id=recipe_id).exists():
                recipe = recipe.first()
                shop_list.remove(recipe)
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error='Рецепт не был добавлен в список покупок')
            )
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data=dict(error='Рецепт не найден')
        )

    @action(
        methods=('get',), detail=False,
        url_path='download_shopping_cart',
        **AUTH
    )
    def download_shop_list(self, request):
        current_user = request.user
        recipes = current_user.shop_list.recipes.all()
        return download_csv(recipes)

    @action(
        methods=('post',), detail=False,
        url_path='(?P<recipe_id>[^/.]+)/favorite',
        **AUTH
    )
    def add_to_favorite(self, request, recipe_id):
        current_user = request.user
        recipe = Recipe.objects.filter(id=recipe_id)
        if recipe.exists():
            favorite = current_user.favorite.recipes
            if favorite.filter(id=recipe_id).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=dict(error='Уже добавлено')
                )
            recipe = recipe.first()
            favorite.add(recipe)
            serializer = RecipeInSerializer(recipe)
            return Response(
                status=status.HTTP_201_CREATED,
                data=serializer.data
            )
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data=dict(error='Рецепт не найден')
        )

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, recipe_id):
        current_user = request.user
        recipe = Recipe.objects.filter(id=recipe_id)
        if recipe.exists():
            favorite = current_user.favorite.recipes
            if favorite.filter(id=recipe_id).exists():
                recipe = recipe.first()
                favorite.remove(recipe)
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error='Рецепт не был добавлен в список покупок')
            )
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data=dict(error='Рецепт не найден')
        )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        if self.get_object().author == request.user:
            return super().update(request, *args, **kwargs)
        return Response(
            status=status.HTTP_403_FORBIDDEN,
            data=dict(detail="Нет доступа")
        )

    def destroy(self, request, *args, **kwargs):
        if self.get_object().author == request.user:
            return super().destroy(request, *args, **kwargs)
        return Response(
            status=status.HTTP_403_FORBIDDEN,
            data=dict(detail="Нет доступа")
        )
