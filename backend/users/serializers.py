"""

    @ File: serializers.py
    @ Date: 18.12.2022
    @ Author: Ohlupin Maxim

"""
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class PasswordSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        raise NotImplementedError('Нельзя использовать для обновления')

    def create(self, validated_data):
        raise NotImplementedError('Нельзя использовать для создания')

    def validate(self, attrs):
        new_password = attrs['new_password']
        current_password = attrs['current_password']
        if self.instance.check_password(current_password):
            return dict(password=new_password)
        raise serializers.ValidationError(
            dict(current_password="Некорректное значение.")
        )

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_('email'),
        write_only=True
    )
    password = serializers.CharField(
        label=_('password'),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_('Token'),
        read_only=True
    )

    def update(self, instance, validated_data):
        raise NotImplementedError('Нельзя использовать для обновления')

    def create(self, validated_data):
        raise NotImplementedError('Нельзя использовать для создания')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email, password=password
            )
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
