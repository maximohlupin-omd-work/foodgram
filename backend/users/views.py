from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from .models import User

from .serializers import AuthTokenSerializer
from .serializers import PasswordSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]
    queryset = User.objects.all()
    serializer_class = ...

    @action(detail=False, methods=['post'], url_path='set_password')
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
                token = Token.objects.filter(key=auth[7:])
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
