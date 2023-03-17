from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.db.models import Exists
from django.db.models import OuterRef

from users.permissions import IsAuthOrReadOnly

from .models import Recipe
from .models import IngredientUnit

from .serializers import RecipeSerializer
from .serializers import RecipeInSerializer
from .serializers import IngredientUnitSerializer

from .utils import download_csv

AUTH = dict(
    permission_classes=[IsAuthenticated, ],
    authentication_classes=[TokenAuthentication, ]
)


class IngredientUnitViewSet(viewsets.ModelViewSet):
    queryset = IngredientUnit.objects.all()
    serializer_class = IngredientUnitSerializer
    http_method_names = ('get',)

    def get_queryset(self):
        query_params = self.request.query_params

        name_filter = query_params.get("name")
        if name_filter:
            return self.get_queryset().filter(
                name__startswith=name_filter
            )

        return self.get_queryset()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            current_user = self.request.user
            return self.queryset.annotate(
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
        return self.queryset

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
# def create(self, request, *args, **kwargs):
#     if request.user.is_authenticated:
#         data = request.data
#         image = data["image"]
#     return Response(status=401)
