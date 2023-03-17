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
from recipes.models import Favorite

from .models import User
from .models import SubscribeUser


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        ShopList.objects.create(author=instance)
        Favorite.objects.create(author=instance)
        SubscribeUser.objects.create(owner=instance)
