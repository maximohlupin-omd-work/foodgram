from rest_framework import viewsets

from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated

from rest_framework.authentication import TokenAuthentication

from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeSerializer
from .serializers import RecipeInShopListSerializer

AUTH = dict(
    permission_classes=[IsAuthenticated, ],
    authentication_classes=[TokenAuthentication, ]
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)

    @action(
        methods=('post',), detail=False,
        url_path='(?P<recipe_id>[^/.]+)/shopping_cart',
        **AUTH
    )
    def add_in_shop_list(self, request, recipe_id):
        ...

    # def create(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         data = request.data
    #         image = data["image"]
    #     return Response(status=401)
