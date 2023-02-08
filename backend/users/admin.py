from django.contrib import admin

from .models import User
from .models import SubscribeUser


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "date_joined")


class SubscribeUserAdmin(admin.ModelAdmin):
    list_display = ("owner", )


admin.site.register(User, UserAdmin)
admin.site.register(SubscribeUser, SubscribeUserAdmin)
