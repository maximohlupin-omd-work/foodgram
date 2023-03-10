from django.db import models

from django.contrib.auth import models as auth_models

from rest_framework.authtoken.models import Token


class User(auth_models.AbstractUser):
    email = models.EmailField(verbose_name="Email Address", unique=True)
    username = models.CharField(verbose_name="username", max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", ]

    @property
    def is_authenticated(self):
        return Token.objects.filter(user=self).exists()

    def __str__(self):
        return f"{self.pk}_{self.username}"

    class Meta:
        ordering = ('-id',)


class SubscribeUser(models.Model):
    owner = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        related_name="subscribe_model",
        on_delete=models.CASCADE
    )
    subscriber = models.ManyToManyField(
        User,
        verbose_name="Подписки пользователя",
        related_name="user_subscriptions",
        blank=True
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки на пользователей"
