from rest_framework import status
from rest_framework import viewsets

from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.permissions import IsAuthenticated

from rest_framework.authentication import TokenAuthentication

from rest_framework.decorators import action

from django.db.models import Exists
from django.db.models import OuterRef

from .models import User
from .models import SubscribeUser

from .serializers import AuthTokenSerializer
from .serializers import PasswordSerializer
from .serializers import UserSerializer

AUTH = dict(
    permission_classes=[IsAuthenticated, ],
    authentication_classes=[TokenAuthentication, ]
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_anonymous:
            return self.queryset
        queryset = self.queryset.annotate(
            is_subscribed=Exists(
                SubscribeUser.objects.filter(
                    owner=self.request.user,
                    subscriber=OuterRef("pk")
                )
            )
        )
        return queryset

    @action(detail=False, methods=['get'], url_path='me', **AUTH)
    def get_current_user(self, request):
        serializer = self.serializer_class(instance=request.user)
        data = serializer.data
        data["is_subscribed"] = False
        return Response(data)

    @action(detail=False, methods=['post'], url_path='set_password', **AUTH)
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenUserAuth(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

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
