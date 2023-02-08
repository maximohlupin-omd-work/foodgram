from django.db.models import Exists

from rest_framework import viewsets
from rest_framework import response
from rest_framework.generics import get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User

from .serializers import AuthTokenSerializer


class TokenUserAuth(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        use_request = request.path.split("/")[-2]
        if use_request == "login":
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'auth_token': token.key,
            })
        elif use_request == "logout":
            auth = request.headers.get("Authorization")
            if auth:
                token = Token.objects.filter(key=auth[7:])
                if token.exists():
                    token.delete()
                    return Response(status=204)
                return Response(
                    status=404,
                    data=dict(
                        detail="Учетные данные не найдены"
                    )
                )
            return Response(
                status=401,
                data=dict(
                    detail="Учетные данные не были предоставлены."
                )
            )
