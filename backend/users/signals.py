"""

    @ File: signals.py
    @ Date: 09.02.2023
    @ Author: Ohlupin Maxim

"""
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework.authtoken.models import Token

from recipes.models import ShopList

from .models import SubscribeUser


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(_, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        ShopList.objects.create(author=instance)
        SubscribeUser.objects.create(owner=instance)
