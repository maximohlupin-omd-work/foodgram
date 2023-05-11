from rest_framework import status
from rest_framework import viewsets

from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.authentication import TokenAuthentication

from rest_framework.decorators import action

from django.db.models import Count
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import ObjectDoesNotExist

from .models import User
from .models import SubscribeUser

from .permissions import IsAuthOrReadOnly

from .serializers import SubscriptionsSerializer
from .serializers import AuthTokenSerializer
from .serializers import PasswordSerializer
from .serializers import UserSerializer

AUTH = dict(
    permission_classes=(IsAuthenticated,),
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthOrReadOnly,)
    http_method_names = ('get', 'post', 'delete',)

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_authenticated:
            queryset = self.queryset.exclude(
                id=current_user.id
            ).annotate(
                is_subscribed=Exists(
                    SubscribeUser.objects.filter(
                        owner=current_user,
                        subscriber=OuterRef('id')
                    )
                )
            )
            return queryset
        return self.queryset

    def get_permissions(self):
        if self.action == 'create':
            return AllowAny(),
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='me', **AUTH)
    def get_current_user(self, request):
        serializer = self.serializer_class(instance=request.user)
        data = serializer.data
        data["is_subscribed"] = False
        return Response(data)

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions', **AUTH)
    def subscriptions(self, request):
        queryset = request.user.subscribe_model.subscriber.annotate(
            recipes_count=Count('recipes')
        ).order_by('-id')

        page = self.paginate_queryset(queryset)

        query_params = request.query_params
        recipes_limit = query_params.get("recipes_limit")
        context = dict(recipes_limit=recipes_limit)

        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context=context
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(
            queryset, many=True, context=context
        )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_destroy(self, instance):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=('post',), detail=False,
        url_path='(?P<subscribe_id>[^/.]+)/subscribe',
        **AUTH
    )
    def subscribe(self, request, subscribe_id: int):
        user_id = request.user.id
        if user_id == int(subscribe_id):
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=dict(
                    errors='Нельзя подписаться на самого себя'
                )
            )
        another_user = User.objects.filter(id=subscribe_id)
        if another_user.exists():
            another_user = another_user.annotate(
                recipes_count=Count('recipes')
            ).first()
            try:
                subscribe_model = request.user.subscribe_model.subscriber
                if subscribe_model.filter(id=another_user.id).exists():
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data=dict(detail="Подписка уже создана!")
                    )
                subscribe_model.add(another_user)
            except ObjectDoesNotExist:
                subscribe_model = SubscribeUser.objects.create(
                    owner=request.user
                )
                subscribe_model.subscriber.add(another_user)

            serializer = SubscriptionsSerializer(another_user)

            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data=dict(detail='Страница не найдена.')
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, subscribe_id: int):
        user_id = request.user.id
        if user_id == int(subscribe_id):
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=dict(
                    errors='Нельзя отписаться от самого себя'
                )
            )
        another_user = User.objects.filter(id=subscribe_id)
        if another_user.exists():
            another_user = another_user.first()
            try:
                subscribe_model = request.user.subscribe_model.subscriber
                if subscribe_model.filter(id=another_user.id).exists():
                    subscribe_model.remove(another_user)
                    return Response(
                        status=status.HTTP_204_NO_CONTENT,
                    )
            except ObjectDoesNotExist:
                ...
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data=dict(detail='Страница не найдена.')
        )


class TokenUserAuth(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    http_method_names = ["post", ]

    def post(self, request, *args, **kwargs):
        use_request = request.path.split('/')[-2]
        if use_request == 'login':
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'auth_token': token.key,
            })
        elif use_request == 'logout':
            auth = request.headers.get('Authorization')
            if auth:
                token = Token.objects.filter(key=auth[6:])
                if token.exists():
                    token.delete()
                    return Response(status=204)
                return Response(
                    status=404,
                    data=dict(
                        detail='Учетные данные не найдены'
                    )
                )
            return Response(
                status=401,
                data=dict(
                    detail='Учетные данные не были предоставлены.'
                )
            )
