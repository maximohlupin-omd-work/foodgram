"""

    @ File: urls.py
    @ Date: 18.12.2022
    @ Author: Ohlupin Maxim

"""
from django.urls import path
from django.urls import re_path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    re_path(r'^auth/token/(login|logout)/', views.TokenUserAuth.as_view()),
    *router.urls
]
