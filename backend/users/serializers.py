"""

    @ File: serializers.py
    @ Date: 18.12.2022
    @ Author: Ohlupin Maxim

"""
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from recipes.models import Recipe

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True, default=False)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(
            **validated_data
        )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'password'
        )


class SubscriberRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class SubscriptionsSerializer(UserSerializer):
    # recipes = SubscriberRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            'recipes_count', 'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            # 'recipes'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        recipes_limit = self.context["recipes_limit"]
        if recipes_limit:
            recipes = instance.recipes.all()[:int(recipes_limit)]
        else:
            recipes = instance.recipes.all()
        recipe_serializer = SubscriberRecipeSerializer(recipes, many=True)
        ret["recipes"] = recipe_serializer.data
        return ret


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
            dict(current_password='Некорректное значение.')
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
        label=_("Token"),
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
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
