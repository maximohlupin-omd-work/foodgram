from rest_framework import viewsets

from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated

from rest_framework.authentication import TokenAuthentication

from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeSerializer

AUTH = dict(
    permission_classes=[IsAuthenticated, ],
    authentication_classes=[TokenAuthentication, ]
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)

    # def create(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         data = request.data
    #         image = data["image"]
    #     return Response(status=401)
